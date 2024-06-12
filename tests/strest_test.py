# https://stackoverflow.com/questions/46893226/performance-load-and-stress-testing-in-django
# stress teststing
# locust -f strest_test.py -H http://localhost:49118
# locust -f strest_test.py -H http://85.143.115.145:49118

from locust import HttpUser, task, between
import random
import os

full_path = '/media/newking/LinuxHdd24/MainHDD/work/tifImages'
rel_path = '../tifImages'
PNG_FILES = [os.path.join(rel_path, f) for f in os.listdir(rel_path) if os.path.isfile(os.path.join(rel_path, f))]

class MedmlUser(HttpUser):
  wait_time = between(3, 6)
  # @task
  # def sign_in(self):
  #   res = self.client.get('/sign_in')
  #   print(res)

  @task(1)
  def home(self):
    # raise AttributeError(f"{self._user}")
    header = {
      'Authorization': f"Bearer {self._user['access']}",
      'Content-Type': 'applicatoin/json'
    }
    header_f = {
      'Authorization': f"Bearer {self._user['access']}",
    }
    res = self.client.get('/api/v2/uzi/devices/?format=json', headers=header)
    devices = res.json()

    res = self.client.get('/api/v2/patient/list/?format=json', headers=header)
    patients = res.json()

    uzi_device_id = 1
    proj_types = ['long', 'cross']
    patient_card = 1

    create_data = {
      'uzi_device': uzi_device_id,
      'projection_type': proj_types[random.randint(0,1)],
      'patient_card': patient_card,
    }
    file_path = random.choice(PNG_FILES)
    rand_file = open(file_path, 'rb')

    res = self.client.post(
      '/api/v2/uzi/create/', 
      data=create_data, 
      headers=header_f,
      files={'original_image':rand_file})
    
  @task(1)
  def patients(self):
    header = {
      'Authorization': f"Bearer {self._user['access']}",
      'Content-Type': 'applicatoin/json'
    }
    self.client.get('/api/v2/med_worker/patients/1?format=json', headers=header)
    self.client.get('/api/v2/patient/update/1?format=json', headers=header)
    res = self.client.get('/api/v2/patient/shots/1?format=json', headers=header)
    data = res.json()
    sh = data['results']['shots']
    shot = random.choice(sh)
    res = self.client.get(f'/api/v2/uzi/{shot["id"]}/?format=json', headers=header)
    data = res.json()

    self.client.get(data['images']['original']['image'])
    try:
      self.client.get(data['images']['box']['image'])
    except:
      pass
    try:
      self.client.get(data['images']['segmentation']['image'])
    except:
      pass

  def on_start(self):
    user = {
      'email': 'admin@admin.ad',
      'password': 'admin'
    }
    res = self.client.post('/api/v2/auth/login/', json=user)
    vars = res.json()
    self._user = vars

if __name__ == '__main__':
  print(PNG_FILES)
  file_path = random.choice(PNG_FILES)
  print(file_path)