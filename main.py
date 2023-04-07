import requests

class VK:

   def __init__(self, access_token, user_id, version='5.131'):
       self.token = access_token
       self.id = user_id
       self.version = version
       self.params = {'access_token': self.token, 'v': self.version}

   def users_info(self):
       url = 'https://api.vk.com/method/users.get'
       params = {'user_ids': self.id}
       response = requests.get(url, params={**self.params, **params})
       return response.json()


access_token = 'vk1.a.cBLZYEofgCAZBVVqez8VUGTmzZC1sKBdFO_BL7Fq08J9sstZHpdxfhFOMG4bwI9ZxKsQtk1MbFabQ2gI6GLlxruIFgvm1oacmZRNxHUmbF-xG2iBOiBFoBmSP-hVVrxaRj40u-OPsWgrmdyBU0ufXq5HSYI0lveIpT2QRBtevBH5oC7VUWZqQ-yuDct1TXWxxmouWutUwxxSzGUFPCN61Q'
user_id = '69616967'
vk = VK(access_token, user_id)
print(vk.users_info())
