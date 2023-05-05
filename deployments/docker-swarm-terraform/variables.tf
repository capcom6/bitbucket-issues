variable "swarm-manager-host" {
  type        = string
  sensitive   = true
  description = "Address of swarm manager"
}

variable "app-name" {
  type        = string
  description = "Name of app"
}

variable "app-version" {
  type        = string
  description = "Version of Docker image of app"
  default     = "1.0"
}

variable "app-host" {
  type        = string
  description = "Hostname of app"
  default     = "1.0"
}

variable "app-auth" {
  type      = string
  sensitive = true
}

variable "app-config-b64" {
  type      = string
  sensitive = true
}
