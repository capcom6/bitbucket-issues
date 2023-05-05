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
  type        = string
  description = "User and password in htpasswd format"
  sensitive   = true
}

variable "app-config-b64" {
  type        = string
  description = "Application config file, base64-encoded"
  sensitive   = true
}

variable "cpu-limit" {
  type        = number
  description = "CPU limit in nanoseconds"
  default     = 100000000
}

variable "memory-limit" {
  type        = number
  description = "Memory limit in bytes"
  default     = 128000000
}
