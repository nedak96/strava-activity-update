
variable "strava_client_id" {
  description = "Strava API client ID"
  type        = string
}

variable "strava_client_secret" {
  description = "Strava API client secret"
  type        = string
  # Uncomment to remove from AWS console
  # sensitive   = true
}

variable "strava_initial_refresh_token" {
  description = "Strava API initial refresh token"
  type        = string
  # Uncomment to remove from AWS console
  # sensitive   = true
}

variable "garmin_username" {
  description = "Garmin login email"
  type        = string
}

variable "garmin_password" {
  description = "Garmin login password"
  type        = string
  # Uncomment to remove from AWS console
  # sensitive   = true
}

locals {
  refresh_token_key = "refresh_token"
  access_token_key  = "access_token"
}
