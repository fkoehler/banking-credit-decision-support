resource "random_string" "suffix" {
  length  = 6
  upper   = false
  special = false
}

locals {
  prefix = "bccs-${var.environment}-${random_string.suffix.result}"
  tags = {
    application = "banking-credit-decision-support"
    environment = var.environment
    data        = "synthetic-only"
    managed-by  = "terraform"
  }
  private_dns_zones = {
    acr          = "privatelink.azurecr.io"
    openai       = "privatelink.openai.azure.com"
    key_vault    = "privatelink.vaultcore.azure.net"
    storage_blob = "privatelink.blob.core.windows.net"
    storage_file = "privatelink.file.core.windows.net"
    ml_api       = "privatelink.api.azureml.ms"
    ml_notebooks = "privatelink.notebooks.azure.net"
  }
}

resource "azurerm_resource_group" "main" {
  name     = "rg-${local.prefix}"
  location = var.location
  tags     = local.tags
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = "log-${local.prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.tags
}

resource "azurerm_container_registry" "main" {
  name                          = replace("acr${local.prefix}", "-", "")
  resource_group_name           = azurerm_resource_group.main.name
  location                      = azurerm_resource_group.main.location
  sku                           = "Premium"
  admin_enabled                 = false
  public_network_access_enabled = false
  zone_redundancy_enabled       = false
  tags                          = local.tags
}

resource "azurerm_virtual_network" "main" {
  name                = "vnet-${local.prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = ["10.42.0.0/16"]
  tags                = local.tags
}

resource "azurerm_subnet" "aks" {
  name                 = "snet-aks"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.42.0.0/20"]
}

resource "azurerm_subnet" "postgres" {
  name                 = "snet-postgres"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.42.16.0/24"]
  delegation {
    name = "postgres-flexible-server"
    service_delegation {
      name    = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

resource "azurerm_subnet" "private_endpoints" {
  name                 = "snet-private-endpoints"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.42.17.0/24"]
}

resource "azurerm_private_dns_zone" "services" {
  for_each = local.private_dns_zones

  name                = each.value
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "services" {
  for_each = local.private_dns_zones

  name                  = "${each.key}-vnet-link"
  private_dns_zone_name = azurerm_private_dns_zone.services[each.key].name
  virtual_network_id    = azurerm_virtual_network.main.id
  resource_group_name   = azurerm_resource_group.main.name
}

resource "azurerm_private_dns_zone" "postgres" {
  name                = "${local.prefix}.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "postgres" {
  name                  = "postgres-vnet-link"
  private_dns_zone_name = azurerm_private_dns_zone.postgres.name
  virtual_network_id    = azurerm_virtual_network.main.id
  resource_group_name   = azurerm_resource_group.main.name
}

resource "azurerm_postgresql_flexible_server" "main" {
  name                          = "psql-${local.prefix}"
  resource_group_name           = azurerm_resource_group.main.name
  location                      = azurerm_resource_group.main.location
  version                       = "16"
  delegated_subnet_id           = azurerm_subnet.postgres.id
  private_dns_zone_id           = azurerm_private_dns_zone.postgres.id
  public_network_access_enabled = false
  administrator_login           = var.postgres_admin_username
  administrator_password        = var.postgres_admin_password
  zone                          = "1"
  storage_mb                    = 32768
  sku_name                      = "B_Standard_B1ms"
  backup_retention_days         = 7
  tags                          = local.tags

  authentication {
    active_directory_auth_enabled = false
    password_auth_enabled         = true
  }

  depends_on = [azurerm_private_dns_zone_virtual_network_link.postgres]
}

resource "azurerm_postgresql_flexible_server_database" "application" {
  name      = "bank_credit_support"
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "UTF8"
}

resource "azurerm_postgresql_flexible_server_configuration" "extensions" {
  name      = "azure.extensions"
  server_id = azurerm_postgresql_flexible_server.main.id
  value     = "VECTOR"
}

resource "azurerm_key_vault" "main" {
  name                          = "kv-${local.prefix}"
  location                      = azurerm_resource_group.main.location
  resource_group_name           = azurerm_resource_group.main.name
  tenant_id                     = var.tenant_id
  sku_name                      = "standard"
  rbac_authorization_enabled    = true
  purge_protection_enabled      = true
  soft_delete_retention_days    = 7
  public_network_access_enabled = false
  tags                          = local.tags
}

resource "azurerm_cognitive_account" "openai" {
  name                          = "oai-${local.prefix}"
  location                      = azurerm_resource_group.main.location
  resource_group_name           = azurerm_resource_group.main.name
  kind                          = "OpenAI"
  sku_name                      = "S0"
  custom_subdomain_name         = "oai-${local.prefix}"
  local_auth_enabled            = false
  public_network_access_enabled = false
  tags                          = local.tags
}

resource "azurerm_cognitive_deployment" "chat" {
  name                 = "chat"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  model {
    format  = "OpenAI"
    name    = var.openai_chat_model
    version = var.openai_chat_model_version
  }
  sku {
    name     = "GlobalStandard"
    capacity = 10
  }
}

resource "azurerm_cognitive_deployment" "embeddings" {
  name                 = "embeddings"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  model {
    format  = "OpenAI"
    name    = var.openai_embedding_model
    version = var.openai_embedding_model_version
  }
  sku {
    name     = "Standard"
    capacity = 10
  }
}

resource "azurerm_storage_account" "ml" {
  name                          = replace("st${local.prefix}", "-", "")
  resource_group_name           = azurerm_resource_group.main.name
  location                      = azurerm_resource_group.main.location
  account_tier                  = "Standard"
  account_replication_type      = "LRS"
  min_tls_version               = "TLS1_2"
  public_network_access_enabled = false
  tags                          = local.tags
}

resource "azurerm_application_insights" "ml" {
  name                = "appi-${local.prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  tags                = local.tags
}

resource "azurerm_machine_learning_workspace" "main" {
  name                          = "mlw-${local.prefix}"
  location                      = azurerm_resource_group.main.location
  resource_group_name           = azurerm_resource_group.main.name
  application_insights_id       = azurerm_application_insights.ml.id
  key_vault_id                  = azurerm_key_vault.main.id
  storage_account_id            = azurerm_storage_account.ml.id
  public_network_access_enabled = false
  high_business_impact          = true
  tags                          = local.tags
  identity { type = "SystemAssigned" }
}

resource "azurerm_private_endpoint" "acr" {
  name                = "pe-acr-${local.prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.private_endpoints.id
  tags                = local.tags

  private_service_connection {
    name                           = "acr"
    private_connection_resource_id = azurerm_container_registry.main.id
    subresource_names              = ["registry"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "acr"
    private_dns_zone_ids = [azurerm_private_dns_zone.services["acr"].id]
  }
}

resource "azurerm_private_endpoint" "openai" {
  name                = "pe-openai-${local.prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.private_endpoints.id
  tags                = local.tags

  private_service_connection {
    name                           = "openai"
    private_connection_resource_id = azurerm_cognitive_account.openai.id
    subresource_names              = ["account"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "openai"
    private_dns_zone_ids = [azurerm_private_dns_zone.services["openai"].id]
  }
}

resource "azurerm_private_endpoint" "key_vault" {
  name                = "pe-key-vault-${local.prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.private_endpoints.id
  tags                = local.tags

  private_service_connection {
    name                           = "key-vault"
    private_connection_resource_id = azurerm_key_vault.main.id
    subresource_names              = ["vault"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "key-vault"
    private_dns_zone_ids = [azurerm_private_dns_zone.services["key_vault"].id]
  }
}

resource "azurerm_private_endpoint" "storage" {
  for_each = toset(["blob", "file"])

  name                = "pe-storage-${each.key}-${local.prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.private_endpoints.id
  tags                = local.tags

  private_service_connection {
    name                           = "storage-${each.key}"
    private_connection_resource_id = azurerm_storage_account.ml.id
    subresource_names              = [each.key]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "storage-${each.key}"
    private_dns_zone_ids = [azurerm_private_dns_zone.services["storage_${each.key}"].id]
  }
}

resource "azurerm_private_endpoint" "machine_learning" {
  name                = "pe-ml-${local.prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.private_endpoints.id
  tags                = local.tags

  private_service_connection {
    name                           = "machine-learning"
    private_connection_resource_id = azurerm_machine_learning_workspace.main.id
    subresource_names              = ["amlworkspace"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name = "machine-learning"
    private_dns_zone_ids = [
      azurerm_private_dns_zone.services["ml_api"].id,
      azurerm_private_dns_zone.services["ml_notebooks"].id,
    ]
  }
}

resource "azurerm_kubernetes_cluster" "main" {
  name                      = "aks-${local.prefix}"
  location                  = azurerm_resource_group.main.location
  resource_group_name       = azurerm_resource_group.main.name
  dns_prefix                = "aks-${local.prefix}"
  kubernetes_version        = var.kubernetes_version
  private_cluster_enabled   = true
  oidc_issuer_enabled       = true
  workload_identity_enabled = true
  local_account_disabled    = true
  sku_tier                  = "Standard"

  default_node_pool {
    name                 = "system"
    vm_size              = "Standard_D4ds_v5"
    auto_scaling_enabled = true
    min_count            = 2
    max_count            = 4
    vnet_subnet_id       = azurerm_subnet.aks.id
    os_disk_size_gb      = 64
  }

  identity { type = "SystemAssigned" }

  network_profile {
    network_plugin      = "azure"
    network_plugin_mode = "overlay"
    network_policy      = "cilium"
    network_data_plane  = "cilium"
    service_cidr        = "10.43.0.0/16"
    dns_service_ip      = "10.43.0.10"
  }

  key_vault_secrets_provider {
    secret_rotation_enabled = true
  }

  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  }
  tags = local.tags
}

resource "azurerm_role_assignment" "aks_acr_pull" {
  scope                = azurerm_container_registry.main.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
}

resource "azurerm_user_assigned_identity" "api" {
  name                = "id-api-${local.prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.tags
}

resource "azurerm_user_assigned_identity" "ai" {
  name                = "id-ai-${local.prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.tags
}

resource "azurerm_federated_identity_credential" "api" {
  name                = "api-service-account"
  resource_group_name = azurerm_resource_group.main.name
  parent_id           = azurerm_user_assigned_identity.api.id
  audience            = ["api://AzureADTokenExchange"]
  issuer              = azurerm_kubernetes_cluster.main.oidc_issuer_url
  subject             = "system:serviceaccount:banking-credit-support:banking-api"
}

resource "azurerm_federated_identity_credential" "ai" {
  name                = "ai-service-account"
  resource_group_name = azurerm_resource_group.main.name
  parent_id           = azurerm_user_assigned_identity.ai.id
  audience            = ["api://AzureADTokenExchange"]
  issuer              = azurerm_kubernetes_cluster.main.oidc_issuer_url
  subject             = "system:serviceaccount:banking-credit-support:ai-service"
}

resource "azurerm_role_assignment" "ai_openai" {
  scope                = azurerm_cognitive_account.openai.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = azurerm_user_assigned_identity.ai.principal_id
}

resource "azurerm_role_assignment" "api_key_vault" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.api.principal_id
}

resource "azurerm_role_assignment" "ai_key_vault" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.ai.principal_id
}
