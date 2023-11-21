
variable "strava_client_id" {
  description = "Strava API client ID"
  type        = string
}

variable "strava_client_secret" {
  description = "Strava API client secret"
  type        = string
}

variable "strava_initial_refresh_token" {
  description = "Strava API initial refresh token"
  type        = string
}

variable "garmin_username" {
  description = "Garmin login email"
  type        = string
}

variable "garmin_password" {
  description = "Garmin login password"
  type        = string
}

locals {
  refresh_token_key = "refresh_token"
  access_token_key  = "access_token"
}
