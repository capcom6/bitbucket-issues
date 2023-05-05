data "docker_registry_image" "bitbucket-issues" {
  name = "capcom6/${var.app-name}:${var.app-version}"
}

data "docker_network" "proxy" {
  name = "proxy"
}


resource "docker_image" "app" {
  name          = data.docker_registry_image.bitbucket-issues.name
  pull_triggers = [data.docker_registry_image.bitbucket-issues.sha256_digest]
  keep_locally  = true
}

resource "docker_config" "app" {
  name = "${var.app-name}-config.yml-${replace(timestamp(), ":", ".")}"
  data = var.app-config-b64

  lifecycle {
    ignore_changes        = [name]
    create_before_destroy = true
  }
}

resource "docker_service" "app" {
  name = var.app-name

  task_spec {
    container_spec {
      image = docker_image.app.image_id

      configs {
        config_id   = docker_config.app.id
        config_name = docker_config.app.name
        file_name   = "/app/config.yml"
      }
    }
    networks_advanced {
      name = data.docker_network.proxy.id
    }

    resources {
      limits {
        nano_cpus    = var.cpu-limit
        memory_bytes = var.memory-limit
      }

      reservation {
        nano_cpus    = 100000000
        memory_bytes = 64000000
      }
    }
  }

  labels {
    label = "traefik.enable"
    value = true
  }

  labels {
    label = "traefik.http.middlewares.${var.app-name}-auth.basicauth.users"
    value = var.app-auth
  }

  labels {
    label = "traefik.http.routers.${var.app-name}.middlewares"
    value = "${var.app-name}-auth"
  }

  labels {
    label = "traefik.http.routers.${var.app-name}.rule"
    value = "Host(`${var.app-host}`)"
  }
  labels {
    label = "traefik.http.routers.${var.app-name}.entrypoints"
    value = "https"
  }
  labels {
    label = "traefik.http.routers.${var.app-name}.tls"
    value = true
  }
  labels {
    label = "traefik.http.services.${var.app-name}.loadbalancer.server.port"
    value = 8000
  }
}
