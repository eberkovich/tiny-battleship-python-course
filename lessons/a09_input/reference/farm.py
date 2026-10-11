print("Сколько животных на ферме?")
answer = input()
animals = int(answer)
print("Сколько у них ног?")
answer = input()
legs = int(answer)
extra_legs = legs - animals * 2
sheep = extra_legs // 2
hens = animals - sheep
print(hens)
print(sheep)
