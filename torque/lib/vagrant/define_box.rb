# Name: define_box.rb ile  environment.conf  hiera.yaml  lib                 observr-cfg.rb  rsgw
# Author: ICS-ACI Infrastructure Team <aci-systems-team@ics.psu.edu>im Vagrantfile
# Description: This set of defined functions sets up reusable vagrant box
#   defines that allow for rapid iteratioon and deployment in the ICS-ACI
#   development environment.

# configureCent6: CentOS 6 ICS Vagrant Server
def configureCent6(configobj)
  configobj.vm.box_url = "https://artifactory.int.aci.ics.psu.edu/artifactory/ics_vagrant/centos6.json"
  configobj.vm.box = "ics/centos6"
end
  
# configureCent7: CentOS 7 ICS Vagrant Server
def configureCent7(configobj)
  configobj.vm.box_url = "https://artifactory.int.aci.ics.psu.edu/artifactory/ics_vagrant/centos7.json"
  configobj.vm.box = "ics/centos7"
end

# configureRHEL6: RHEL 6 ICS Vagrant Server
def configureRhel6(configobj)
  configobj.vm.box_url = "https://artifactory.int.aci.ics.psu.edu/artifactory/ics_vagrant/rhel6.box"
  configobj.vm.box = "ics/rhel6"
end

# configureRhel7: RHEL 7 ICS Vagrant Server
def configureRhel7(configobj)
  configobj.vm.box_url = "https://artifactory.int.aci.ics.psu.edu/artifactory/ics_vagrant/rhel7.box"
  configobj.vm.box = "ics/rhel7"
end

# configureRhel8: RHEL 8 ICS Vagrant Server
def configureRhel8(configobj)
  configobj.vm.box_url = "https://artifactory.int.aci.ics.psu.edu/artifactory/ics_vagrant/rhel8.box"
  configobj.vm.box = "ics/rhel8"
end

def configureSl7(configobj)
  configobj.vm.box_url = "https://artifactory.int.aci.ics.psu.edu/artifactory/ics_vagrant/sl7.json"
  configobj.vm.box = "ics/sl7"
end
  
def configureVyos(configobj)
  configobj.vm.box_url = "https://artifactory.int.aci.ics.psu.edu/artifactory/ics_vagrant/vyos.json"
  configobj.vm.box = "ics/vyos"
  configobj.vm.synced_folder '.', '/vagrant', disabled: true
end
    