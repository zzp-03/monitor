while True:
    num1 = int(input("请输入第一个数字："))
    num2 = int(input("请输入第二个数字："))
    op = input("请输入运算符:")
    if op == "+":
        print(num1 + num2)
    elif op == "-":
        print(num1 - num2)
    elif op == "*":
        print(num1 * num2)
    elif op == "/":
        print(num1 / num2)
        if num2 == 0:
             print("除数不能为零！")
    else :
        print("请输入正确的运算符！")
    choice = input("是否继续计算:（y/n）")
    if choice == "n":
        break
