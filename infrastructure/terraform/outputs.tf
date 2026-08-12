output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.main.name
}

output "container_registry" {
  value = azurerm_container_registry.main.login_server
}

output "postgres_fqdn" {
  value = azurerm_postgresql_flexible_server.main.fqdn
}

output "azure_openai_endpoint" {
  value = azurerm_cognitive_account.openai.endpoint
}

output "machine_learning_workspace" {
  value = azurerm_machine_learning_workspace.main.name
}

output "api_identity_client_id" {
  value = azurerm_user_assigned_identity.api.client_id
}

output "ai_identity_client_id" {
  value = azurerm_user_assigned_identity.ai.client_id
}
