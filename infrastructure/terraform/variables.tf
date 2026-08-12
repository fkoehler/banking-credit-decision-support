variable "location" {
  description = "Azure region that supports the selected OpenAI models."
  type        = string
  default     = "swedencentral"
}

variable "environment" {
  description = "Short environment name used in resource naming."
  type        = string
  default     = "dev"
}

variable "tenant_id" {
  description = "Microsoft Entra tenant id."
  type        = string
}

variable "postgres_admin_username" {
  description = "Bootstrap PostgreSQL administrator. Applications should use a narrower role."
  type        = string
  default     = "platformadmin"
}

variable "postgres_admin_password" {
  description = "Bootstrap password supplied through a protected TF_VAR variable."
  type        = string
  sensitive   = true
}

variable "kubernetes_version" {
  description = "AKS Kubernetes version approved for the target subscription."
  type        = string
  default     = "1.32"
}

variable "openai_chat_model" {
  description = "Azure OpenAI model name available in the selected region."
  type        = string
  default     = "gpt-4.1-mini"
}

variable "openai_chat_model_version" {
  description = "Explicit Azure OpenAI chat model version."
  type        = string
  default     = "2025-04-14"
}

variable "openai_embedding_model" {
  description = "Azure OpenAI embedding model name."
  type        = string
  default     = "text-embedding-3-small"
}

variable "openai_embedding_model_version" {
  description = "Explicit Azure OpenAI embedding model version."
  type        = string
  default     = "1"
}
