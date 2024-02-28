import pandas

def trading_strat(data, amount=1000):
    nb_assets = len(data.columns)
    w = 1.0/nb_assets
    pos = pandas.DataFrame(index=data.index)
    for col in data.columns:
        pos[col + '_pos'] = amount*w
    return pos

if __name__=='__main__':
    data = pandas.DataFrame({'actif1': [100, 120], 'actif2': [110, 105]})
    pos = trading_strat(data, 1000)
    print(pos)