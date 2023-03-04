terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.45.0"
    }
  }
}

provider "azurerm" {
  features {}
}

variable "plantuml_size_limit" {
  type    = string
  default = "8192"

}

data "azurerm_service_plan" "name" {
  name                = "mt-diagram-service-plan"
  resource_group_name = "mt-diagrams"
}

resource "azurerm_linux_web_app" "main" {
  name                = "mt-plantuml-app-service"
  resource_group_name = data.azurerm_service_plan.name.resource_group_name
  location            = data.azurerm_service_plan.name.location
  service_plan_id     = data.azurerm_service_plan.name.id

  https_only = true

  app_settings = {
    WEBSITES_PORT                   = 8080
    PLANTUML_LIMIT_SIZE             = var.plantuml_size_limit
    DOCKER_REGISTRY_SERVER_USERNAME = ""
    DOCKER_REGISTRY_SERVER_PASSWORD = ""
  }
  site_config {
    always_on = false

    application_stack {
      docker_image     = "plantuml/plantuml-server"
      docker_image_tag = "tomcat"
    }
  }
}
