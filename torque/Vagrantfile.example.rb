# -*- mode: ruby -*-
# vi: set ft=ruby :
# Name: Vagrantfile
# Author: ICS-ACI Infrastructure Team <aci-systems-team@ics.psu.edu>
# Description: Default ICS-ACI Vagrantfile to support local development
#   environment.


# Require outside define for vagrant
require_relative('lib/vagrant/define_box.rb')

Vagrant.configure(2) do |config|

  config.ssh.forward_agent = true

  # Configure virtualbox provider
  config.vm.provider :virtualbox do |v|
    v.customize ["modifyvm", :id, "--memory", 8192]
  end

  # Allow for insecure box download
  config.vm.box_download_insecure = true

  # Check for existence of hiera keys
  # If keys exist, allow for eyaml, otherwise default to no_eyaml
  if File.directory?('./keys')
    config.vm.synced_folder './keys', '/etc/puppetlabs/keys', mount_options: ['dmode=755', 'fmode=755']    hiera_config = 'hiera.yaml'
  else
    hiera_config = 'hiera_noeyaml.yaml'
  end

  # Setup vagrant syncd folder for puppet baseline access
  config.vm.synced_folder '.', '/vagrant', mount_options: ['dmode=755', 'fmode=755']

  # Provision all Vagrant VMs with prepuppet reqts
  config.vm.provision :shell, inline: 'bash /vagrant/scripts/shell/provision.sh /vagrant/scripts/shell/prepuppet', env: { 'HIERA_CONFIG' => hiera_config }

  # Check for vagrant-hostmanager plugin and if found, setup our defaults
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

  # Check for Vagrant Registration Plugin
  unless Vagrant.has_plugin?('vagrant-registration')
    abort 'Please install the registration plugin with "vagrant plugin install vagrant-registration"'
  end

  # Setup Registration Plugin Variables
  reg_serverurl = 'https://titan.int.aci.ics.psu.edu/rhsm'
  reg_baseurl = 'https://titan.int.aci.ics.psu.edu/pulp/repos'
  reg_cacert = './scripts/titan-ca_cert.crt'
  reg_org = 'ICS-ACI'

  ####
  # Temp Patch for RHEL 7.5
  # https://github.com/projectatomic/adb-vagrant-registration/issues/126
  ###
  module SubscriptionManagerMonkeyPatches
    def self.subscription_manager_registered?(machine)
      true if machine.communicate.sudo("/usr/sbin/subscription-manager list --consumed --pool-only | grep -E '^[a-f0-9]{32}$'")
    rescue
      false
    end
  end

  VagrantPlugins::Registration::Plugin.guest_capability 'redhat', 'subscription_manager_registered?' do
    SubscriptionManagerMonkeyPatches
  end

  #
  # Begin Vagrant Box Configurations
  #

  # ICS-ACI Puppet Server All-in-one Config
  config.vm.define "puppet", primary: true do |puppetsrv|
    puppetsrv.vm.hostname = 'puppet.ics.test'
    configureRhel7 puppetsrv
    puppetsrv.vm.provider :virtualbox do |v|
      v.memory = 4096
    end
    puppetsrv.vm.provider :vmware_workstation do |v|
      v.vmx['memsize'] = '4096'
    end
    puppetsrv.vm.network :private_network, ip: '172.16.254.253'
    puppetsrv.registration.name = 'puppetsrv.ics.test'
    puppetsrv.registration.serverurl = reg_serverurl
    puppetsrv.registration.baseurl = reg_baseurl
    puppetsrv.registration.ca_cert = reg_cacert
    puppetsrv.registration.activationkey = 'aci-development-7Server-Vagrant'
    puppetsrv.registration.auto_attach = true
    puppetsrv.registration.org = 'ICS-ACI'
    puppetsrv.vm.provision :shell, inline: 'bash /vagrant/scripts/shell/provision.sh /vagrant/scripts/shell/postpuppet', env: { 'FACTER_environment' => 'vagrant', 'FACTER_role' => 'puppetallinone' }
    puppetsrv.vm.provision "shell", path: "scripts/puppetserver_gem_install.sh", args: "hiera-eyaml deep_merge"
  end

  # ICS-ACI RHEL6 Compute Node
  config.vm.define "comp6", autostart: false do |comp6|
    configureRhel6 comp6
    comp6.vm.provider :virtualbox do |v|
      v.memory = 2048
      v.cpus = 2
    end
    comp6.vm.provider :vmware_workstation do |v|
      v.vmx['memsize'] = '2048'
      v.vmx['numvcpus'] = '2'
    end
    comp6.vm.hostname = 'comp6.ics.test'
    comp6.vm.network :private_network, ip: '172.16.254.213'
    comp6.registration.name = 'comp6.ics.test'
    comp6.registration.serverurl = reg_serverurl
    comp6.registration.baseurl = reg_baseurl
    comp6.registration.ca_cert = reg_cacert
    comp6.registration.activationkey = 'aci-development-6Server-Vagrant'
    comp6.registration.auto_attach = true
    comp6.registration.org = 'ICS-ACI'
    comp6.vm.provision :shell, inline: 'bash /vagrant/scripts/shell/provision.sh /vagrant/scripts/shell/postpuppet', env: { 'FACTER_environment' => 'vagrant', 'FACTER_role' => 'bdt' }
  end

  # ICS-ACI RHEL 7 Compute Node
  config.vm.define "comp7", autostart: false do |comp7|
    configureRhel7 comp7
    comp7.vm.provider :virtualbox do |v|
      v.memory = 2048
      v.cpus = 2
    end
    comp7.vm.provider :vmware_workstation do |v|
      v.vmx['memsize'] = '2048'
      v.vmx['numvcpus'] = '2'
    end
    comp7.vm.hostname = 'comp7.ics.test'
    comp7.vm.network :private_network, ip: '172.16.254.214'
    comp7.registration.name = 'comp7.ics.test'
    comp7.registration.serverurl = reg_serverurl
    comp7.registration.baseurl = reg_baseurl
    comp7.registration.ca_cert = reg_cacert
    comp7.registration.activationkey = 'aci-development-7Server-Vagrant'
    comp7.registration.auto_attach = true
    comp7.registration.org = 'ICS-ACI'
    comp7.vm.provision :shell, inline: 'bash /vagrant/scripts/shell/provision.sh /vagrant/scripts/shell/postpuppet', env: { 'FACTER_environment' => 'vagrant', 'FACTER_role' => 'bdt' }
  end


  # ICS-ACI RHEL 8 Compute Node
  config.vm.define "comp8", autostart: false do |comp8|
    configureRhel8 comp8
    comp8.vm.provider :virtualbox do |v|
      v.memory = 2048
      v.cpus = 2
    end
    comp8.vm.provider :vmware_workstation do |v|
      v.vmx['memsize'] = '2048'
      v.vmx['numvcpus'] = '2'
    end
    comp8.vm.hostname = 'comp8.ics.test'
    comp8.vm.network :private_network, ip: '172.16.254.221'
    comp8.registration.name = 'comp8.ics.test'
    comp8.registration.username = 'abf123ics'
    comp8.registration.password = ''
    #comp8.registration.org = 'ICS-ACI'
    comp8.vm.provision :shell, inline: 'bash /vagrant/scripts/shell/provision.sh /vagrant/scripts/shell/postpuppet', env: { 'FACTER_environment' => 'vagrant', 'FACTER_role' => 'bdt' }
  end

  # ICS-ACI RHEL 6 Security Testing Node
  config.vm.define "sectest6", autostart: false do |sectest6|
    configureRhel6 sectest6
    sectest6.vm.provider :virtualbox do |v|
      v.memory = 4096
    end
    sectest6.vm.provider :vmware_workstation do |v|
      v.vmx['memsize'] = '4096'
    end
    sectest6.vm.network :private_network, ip: '172.16.254.215'
    sectest6.vm.hostname = 'sectest6.ics.test'
    sectest6.registration.name = 'sectest6.ics.test'
    sectest6.registration.serverurl = reg_serverurl
    sectest6.registration.baseurl = reg_baseurl
    sectest6.registration.ca_cert = reg_cacert
    sectest6.registration.activationkey = 'aci-development-6Server-Vagrant'
    sectest6.registration.auto_attach = true
    sectest6.registration.org = 'ICS-ACI'
    sectest6.vm.provision :shell, inline: 'bash /vagrant/scripts/shell/provision.sh /vagrant/scripts/shell/postpuppet', env: { 'FACTER_environment' => 'vagrant', 'FACTER_role' => 'sectest' }
  end

  # ICS-ACI RHEL 7 Security Testing Node
  config.vm.define "sectest7", autostart: false do |sectest7|
    configureRhel7 sectest7
    sectest7.vm.provider :virtualbox do |v|
      v.memory = 4096
    end
    sectest7.vm.provider :vmware_workstation do |v|
      v.vmx['memsize'] = '4096'
    end
    sectest7.vm.network :private_network, ip: '172.16.254.216'
    sectest7.vm.hostname = 'sectest7.ics.test'
    sectest7.registration.name = 'sectest7.ics.test'
    sectest7.registration.serverurl = reg_serverurl
    sectest7.registration.baseurl = reg_baseurl
    sectest7.registration.ca_cert = reg_cacert
    sectest7.registration.activationkey = 'aci-development-7Server-Vagrant'
    sectest7.registration.auto_attach = true
    sectest7.registration.org = 'ICS-ACI'
    sectest7.vm.provision :shell, inline: 'bash /vagrant/scripts/shell/provision.sh /vagrant/scripts/shell/postpuppet', env: { 'FACTER_environment' => 'vagrant', 'FACTER_role' => 'sectest' }
  end

  # ICS-ACI RHEL 6 HPC Submit Node
  config.vm.define "submit6", autostart: false do |submit6|
    configureRhel6 submit6
    submit6.vm.provider :virtualbox do |v|
      v.memory = 4096
    end
    submit6.vm.provider :vmware_workstation do |v|
      v.vmx['memsize'] = '4096'
    end
    submit6.vm.hostname = 'submit6.ics.test'
    submit6.vm.network :private_network, ip: '172.16.254.217'
    submit6.registration.name = 'submit6.ics.test'
    submit6.registration.serverurl = reg_serverurl
    submit6.registration.baseurl = reg_baseurl
    submit6.registration.ca_cert = reg_cacert
    submit6.registration.activationkey = 'aci-development-6Server-Vagrant'
    submit6.registration.auto_attach = true
    submit6.registration.org = 'ICS-ACI'
    submit6.vm.provision :shell, inline: 'bash /vagrant/scripts/shell/provision.sh /vagrant/scripts/shell/postpuppet', env: { 'FACTER_environment' => 'vagrant', 'FACTER_role' => 'submitnode' }
  end

  # ICS-ACI RHEL 7 HPC Submit Node
  config.vm.define "submit7", autostart: false do |submit7|
    configureRhel7 submit7
    submit7.vm.provider :virtualbox do |v|
      v.memory = 4096
    end
    submit7.vm.provider :vmware_workstation do |v|
      v.vmx['memsize'] = '4096'
    end
    submit7.vm.hostname = 'submit7.ics.test'
    submit7.vm.network :private_network, ip: '172.16.254.218'
    submit7.registration.name = 'submit7.ics.test'
    submit7.registration.serverurl = reg_serverurl
    submit7.registration.baseurl = reg_baseurl
    submit7.registration.ca_cert = reg_cacert
    submit7.registration.activationkey = 'aci-development-7Server-Vagrant'
    submit7.registration.auto_attach = true
    submit7.registration.org = 'ICS-ACI'
    submit7.vm.provision :shell, inline: 'bash /vagrant/scripts/shell/provision.sh /vagrant/scripts/shell/postpuppet', env: { 'FACTER_environment' => 'vagrant', 'FACTER_role' => 'submitnode' }
  end

  # ICS-ACI RHEL 6 Galaxy Test VM
  config.vm.define "galaxygw", autostart: false do |galaxygw|
    configureRhel6 galaxygw
    galaxygw.vm.provider :virtualbox do |v|
      v.memory = 4096
      v.cpus = 2
    end
    galaxygw.vm.provider :vmware_workstation do |v|
      v.vmx['memsize'] = '4096'
      v.vmx['numvcpus'] = '2'
    end
    galaxygw.vm.hostname = 'galaxygw.ics.test'
    galaxygw.vm.network :private_network, ip: '172.16.254.108'
    galaxygw.registration.name = 'galaxygw.ics.test'
    galaxygw.registration.serverurl = reg_serverurl
    galaxygw.registration.baseurl = reg_baseurl
    galaxygw.registration.ca_cert = reg_cacert
    galaxygw.registration.activationkey = 'aci-development-6Server-Vagrant'
    galaxygw.registration.auto_attach = true
    galaxygw.registration.org = 'ICS-ACI'
    galaxygw.vm.provision :shell, inline: 'bash /vagrant/scripts/shell/provision.sh /vagrant/scripts/shell/postpuppet', env: { 'FACTER_environment' => 'vagrant', 'FACTER_role' => 'galaxygw' }
  end

  # ICS-ACI RHEL 6 Interactive Test Node
  config.vm.define "interactive6", autostart: false do |interactive6|
    configureRhel6 interactive6
    interactive6.vm.provider :virtualbox do |v|
      v.memory = 4096
    end
    interactive6.vm.provider :vmware_workstation do |v|
      v.vmx['memsize'] = '4096'
    end
    interactive6.vm.hostname = 'interactive6.ics.test'
    interactive6.vm.network :private_network, ip: '172.16.254.219'
    interactive6.registration.name = 'interactive6.ics.test'
    interactive6.registration.serverurl = reg_serverurl
    interactive6.registration.baseurl = reg_baseurl
    interactive6.registration.ca_cert = reg_cacert
    interactive6.registration.activationkey = 'aci-development-6Server-Vagrant'
    interactive6.registration.auto_attach = true
    interactive6.registration.org = 'ICS-ACI'
    interactive6.vm.provision :shell, inline: 'bash /vagrant/scripts/shell/provision.sh /vagrant/scripts/shell/postpuppet', env: { 'FACTER_environment' => 'vagrant', 'FACTER_role' => 'interactive' }
  end

  # ICS-ACI RHEL 7 Interactive Test Node
  config.vm.define "interactive7", autostart: false do |interactive7|
    configureRhel7 interactive7
    interactive7.vm.provider :virtualbox do |v|
      v.memory = 4096
    end
    interactive7.vm.provider :vmware_workstation do |v|
      v.vmx['memsize'] = '4096'
    end
    interactive7.vm.hostname = 'interactive7.ics.test'
    interactive7.vm.network :private_network, ip: '172.16.254.220'
    interactive7.registration.name = 'interactive7.ics.test'
    interactive7.registration.serverurl = reg_serverurl
    interactive7.registration.baseurl = reg_baseurl
    interactive7.registration.ca_cert = reg_cacert
    interactive7.registration.activationkey = 'aci-development-7Server-Vagrant'
    interactive7.registration.auto_attach = true
    interactive7.registration.org = 'ICS-ACI'
    interactive7.vm.provision :shell, inline: 'bash /vagrant/scripts/shell/provision.sh /vagrant/scripts/shell/postpuppet', env: { 'FACTER_environment' => 'vagrant', 'FACTER_role' => 'interactive' }
  end
end