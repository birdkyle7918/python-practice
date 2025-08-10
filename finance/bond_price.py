"""
    计算债券的新价格（假设当初发行时的票面价格为100元）
    old_interest_rate：老利率，当初发行时的票面利率
    new_interest_rate：新利率，当前发行同一张债券的利率
    remain_time：当初的债券剩余的到期时间，以年为单位
"""
def calculate_current_bond_price(old_interest_rate, new_interest_rate, remain_time):

    # 剩余的小数部分
    decimal_part =  remain_time - int(remain_time)

    # 每年得到的利息收入
    yearly_interest = old_interest_rate * 100

    # 指数
    if decimal_part != 0:
        step = decimal_part
    else:
        step = 1

    # 总价格
    total_price = 0

    # 循环
    while step <= remain_time:
        if step != remain_time:
            yearly_income = yearly_interest
        else:
            yearly_income = 100 + yearly_interest

        total_price += yearly_income / ((1 + new_interest_rate) ** step)
        step += 1

    print(total_price)


if __name__ == '__main__':
    calculate_current_bond_price(0.0333, 0.02, 27.5)
    pass