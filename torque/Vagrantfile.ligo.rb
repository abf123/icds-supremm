# -*- mode: ruby -*-
# vi: set ft=ruby :

require_relative('./lib/vagrant/define_box.rb')

routerconfig = <<EOF
#!/bin/vbash
source /opt/vyatta/etc/functions/script-template
set service ssh allow-root
commit
save
EOF

fmip = '10.136.28.201'
fmhostname = 'foreman.ligo.test'

Vagrant.configure(2) do |config|

  config.ssh.forward_agent = true

  config.vm.provider :virtualbox do |v|
    v.customize ["modifyvm", :id, "--memory", 1024]
  end
  config.vm.provider :vmware_workstation do |v|
    v.vmx['memsize'] = '1024'
  end

  config.vm.box_download_insecure = true

  abort 'Please install the hostmanager plugin with "vagrant plugin install vagrant-vyos' unless Vagrant.has_plugin?('vagrant-vyos')

  config.vm.synced_folder 'puppet', '/vagrant', mount_options: ['dmode=755', 'fmode=755']

  if Vagrant.has_plugin?('vagrant-hostmanager')
    config.hostmanager.manage_host = true
    config.hostmanager.enabled = true
    config.hostmanager.manage_host = true
    config.hostmanager.ignore_private_ip = false
    config.hostmanager.include_offline = true
    config.hostmanager.manage_guest = false
  else
    abort 'Please install the hostmanager plugin with "vagrant plugin install vagrant-hostmanager"'
  end

  config.vm.define "foreman", primary: true do |foreman|
    configureSl7 foreman
    foreman.vm.hostname = fmhostname
    foreman.vm.provider :virtualbox do |v|
      v.memory = 16384
    end
    foreman.vm.provider :vmware_workstation do |v|
      v.vmx['memsize'] = '16384'
    end
    foreman.vm.network :private_network, ip: fmip, netmask: '255.255.254.0'
    foreman.vm.provision "shell", path: './scripts/install_katello.sh'
  end

  config.vm.define "router", primary: true do |router|
    configureVyos(router)
    router.vm.hostname = "rt1.ligo.text"
    router.vm.provider :virtualbox do |v|
      v.memory = 512
    end
    router.vm.provider :vmware_workstation do |v|
      v.vmx['memsize'] = '512'
    end
    router.vm.network :private_network, ip: '10.136.28.5', netmask: '255.255.254.0'
    router.vm.network :private_network, ip: '10.136.30.5', netmask: '255.255.254.0'
    router.vm.provision :shell, inline: routerconfig
  end

  config.vm.define "sl7mirror", primary: true do |sl7mirror|
    configureSl7 sl7mirror
    _privip = '10.136.28.211'
    sl7mirror.vm.hostname = "sl7mirror.ligo.test"
    sl7mirror.vm.provider :virtualbox do |v|
      v.memory = 4096
    end
    sl7mirror.vm.provider :vmware_workstation do |v|
      v.vmx['memsize'] = '4096'
    end
    sl7mirror.vm.network :private_network, ip: _privip, netmask: '255.255.254.0'
    sl7mirror.vm.provision :ansible, playbook: 'ansible/install_puppet.yml',
        extra_vars: { vgip: _privip, vghostname: sl7mirror.vm.hostname, fmip: fmip, fmhostname: fmhostname  }
  end

  config.vm.define "sl7compute", primary: true do |sl7compute|
    configureSl7 sl7compute
    _privip = '10.136.28.216'
    sl7compute.vm.hostname = "sl7compute.ligo.test"
    sl7compute.vm.provider :virtualbox do |v|
      v.memory = 4096
    end
    sl7compute.vm.provider :vmware_workstation do |v|
      v.vmx['memsize'] = '4096'
    end
    sl7compute.vm.network :private_network, ip: _privip, netmask: '255.255.254.0'
    sl7compute.vm.provision :ansible, playbook: 'ansible/install_puppet.yml',
        extra_vars: { vgip: _privip, vghostname: sl7compute.vm.hostname, fmip: fmip, fmhostname: fmhostname }
  end
end
