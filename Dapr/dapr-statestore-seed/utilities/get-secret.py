from secrets import Secrets

s = Secrets()


result = s.get("server")

print(result.content)
