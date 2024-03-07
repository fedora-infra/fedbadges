# -*- mode: ruby -*-
# vi: set ft=ruby :

ENV['VAGRANT_NO_PARALLEL'] = 'yes'

Vagrant.configure(2) do |config|
  config.hostmanager.enabled = true
  config.hostmanager.manage_host = true
  config.hostmanager.manage_guest = true

  config.vm.define "fedbadges" do |fedbadges|
    fedbadges.vm.box_url = "https://download.fedoraproject.org/pub/fedora/linux/releases/39/Cloud/x86_64/images/Fedora-Cloud-Base-Vagrant-39-1.5.x86_64.vagrant-libvirt.box"
    fedbadges.vm.box = "f39-cloud-libvirt"
    fedbadges.vm.hostname = "fedbadges.tinystage.test"

    fedbadges.vm.synced_folder '.', '/vagrant', disabled: true
    fedbadges.vm.synced_folder ".", "/home/vagrant/fedbadges", type: "sshfs"
    fedbadges.vm.synced_folder "../tahrir-api", "/home/vagrant/tahrir-api", type: "sshfs"
    fedbadges.vm.synced_folder "../tahrir", "/home/vagrant/tahrir", type: "sshfs"

    fedbadges.vm.provider :libvirt do |libvirt|
      libvirt.cpus = 2
      libvirt.memory = 2048
    end

    fedbadges.vm.provision "ansible" do |ansible|
      ansible.playbook = "devel/ansible/playbook.yml"
      ansible.config_file = "devel/ansible/ansible.cfg"
      ansible.verbose = true
    end
  end

end
