ears_price = 17
snacks_price = 23
puffs_price = 31

print("Сколько удлинителей ушей покупаешь?")
ears_answer = input()
ears_count = int(ears_answer)
print("Сколько коробок забастовочных завтраков покупаешь?")
snacks_answer = input()
snacks_count = int(snacks_answer)
print("Сколько карликовых пушистиков покупаешь?")
puffs_answer = input()
puffs_count = int(puffs_answer)

ears_cost = ears_count * ears_price
snacks_cost = snacks_count * snacks_price
puffs_cost = puffs_count * puffs_price
total = ears_cost + snacks_cost + puffs_cost
print(ears_count, ears_cost)
print(snacks_count, snacks_cost)
print(puffs_count, puffs_cost)
print(total)

print("Сколько галлеонов отдаёшь для оплаты?")
galleons_answer = input()
galleons = int(galleons_answer)
print("Сколько сиклей отдаёшь для оплаты?")
sickles_answer = input()
sickles = int(sickles_answer)
print("Сколько кнатов отдаёшь для оплаты?")
knuts_answer = input()
knuts = int(knuts_answer)

sickles_in_galleon = 17
knuts_in_sickle = 29
knuts_in_galleon = sickles_in_galleon * knuts_in_sickle
payment = galleons * knuts_in_galleon + sickles * knuts_in_sickle + knuts
change = payment - total * knuts_in_sickle
change_galleons = change // knuts_in_galleon
change = change - change_galleons * knuts_in_galleon
change_sickles = change // knuts_in_sickle
change_knuts = change - change_sickles * knuts_in_sickle
print(change_galleons, change_sickles, change_knuts)
