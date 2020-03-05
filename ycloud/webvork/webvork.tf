provider "yandex" {
  service_account_key_file     = "/home/sergey/mnt/st1500/Usr/Sergey/TheJob/YandexCloud/Webvork/webvork-terraform-key.json"
  cloud_id  = "b1gbd722dh1ji2mfij3a"
  folder_id = "b1g6g0odfjqvpuhrneau"
  zone      = "ru-central1-a"
}



resource "yandex_compute_instance" "vm-1" {
  name = "webvork2-terraform"

  resources {
    cores  = 2
    memory = 4
    core_fraction = 5
    # gpus = 1
  }

  boot_disk {
    initialize_params {
      image_id = "fd8veme9fg6pbg5ost48"
      size = 30
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.subnet-1.id
    nat       = true
  }

  metadata = {
    ssh-keys = "ubuntu:${file("~/.ssh/id_rsa.pub")}"

  }

  scheduling_policy {
      preemptible = true
    }

}

resource "yandex_container_registry" "default" {
  name      = "webvork-docker-registry"
  # folder_id = "test_folder_id"

  #labels = {
  #  my-label = "my-label-value"
  #}
}


resource "yandex_vpc_network" "network-1" {
  name = "network1"
}

resource "yandex_vpc_subnet" "subnet-1" {
  name           = "subnet1"
  zone           = "ru-central1-a"
  network_id     = yandex_vpc_network.network-1.id
  v4_cidr_blocks = ["192.168.10.0/24"]
}

output "internal_ip_address_vm_1" {
  value = yandex_compute_instance.vm-1.network_interface.0.ip_address
}

output "external_ip_address_vm_1" {
  value = yandex_compute_instance.vm-1.network_interface.0.nat_ip_address
}
