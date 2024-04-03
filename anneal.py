import skrf as rf
import os
import numpy as np
import matplotlib.pyplot as plt
from skrf.calibration import OpenShort

def read_s2p(path):
    lines  = None
    with open(path, 'r') as file:
        lines = file.readlines()

    #print("Original S2P file: \n")

    for i in range(len(lines)):
        line = [element.strip() for element in lines[i].split("\t")]
        #print(line)
        if("! Freq" in line):   
            lines[i] = "! Freq	ReS11	ImS11	ReS21	ImS21	ReS12	ImS12	ReS22	ImS22"
        elif(not('!' in line)):
            while '0' in line:
                line.remove('0')
            lines[i] = ' '.join(line)

    with open(path, 'w') as file:
        for line in lines:
            file.writelines(line  + '\n')
    network = rf.Network(path)
    return network


def calc_S11(antenna, de_embed):

    actual_antenna = de_embed.deembed(antenna)

    #actual_antenna = antenna

    S11 = actual_antenna.s[ : ,0,0]
    S12 = actual_antenna.s[ : ,0,1]
    S21 = actual_antenna.s[ : ,1,0]
    S22 = actual_antenna.s[ : ,1,1]

    S_eq = np.abs((S11+S22-S12-S21)/2)

    return S_eq

def avg(path):

    n  = 0

    files = [filename for filename in os.listdir(path) if os.path.isfile(os.path.join(path, filename))]

    pre_anneal = []
    pre_anneal_open = ""
    pre_anneal_short = ""
    post_anneal = []
    post_anneal_open = ""
    post_anneal_short = ""

    for file in files:
        print(file)
        if "Annealed" in file:
            if('O' in file):
                post_anneal_open = file
            elif('S' in file):
                post_anneal_short = file
            else:
                post_anneal.append(file)
        else:
            if('O' in file):
                pre_anneal_open = file
            elif('S' in file):
                pre_anneal_short = file
            else:
                pre_anneal.append(file)

    if(len(pre_anneal) != len(post_anneal)):
        print("Error! : list sizes are not equal!")
    else:
        print("Good so far")


    print("pre_anneal_open: " , pre_anneal_open)
    print("pre_anneal_short: ", pre_anneal_short)
    print("post_anneal_open: ", post_anneal_open)
    print("post_anneal_short: ", post_anneal_short)

    pre_anneal_open_nw = read_s2p(os.path.join(path, pre_anneal_open))        
    pre_anneal_short_nw = read_s2p(os.path.join(path, pre_anneal_short))
    post_anneal_open_nw = read_s2p(os.path.join(path, pre_anneal_open))
    post_anneal_short_nw = read_s2p(os.path.join(path, pre_anneal_short))


    pre_anneal_dm = OpenShort(dummy_open=pre_anneal_open_nw, dummy_short=pre_anneal_short_nw)
    post_anneal_dm = OpenShort(dummy_open=post_anneal_open_nw, dummy_short=post_anneal_short_nw)




    pre_S11s = []
    post_S11s = []

    for i in range(len(pre_anneal)):
        pre_anneal_antenna_name = os.path.join(path, pre_anneal[i])
        pre_anneal_antenna = read_s2p(pre_anneal_antenna_name)

        # pre_anneal_antenna.plot_s_db()
        # plt.title(pre_anneal_antenna_name)
        # plt.show()

        post_anneal_antenna_name = os.path.join(path, post_anneal[i])
        post_anneal_antenna = read_s2p(post_anneal_antenna_name)


        # post_anneal_antenna.plot_s_db()
        # plt.title(post_anneal_antenna_name)
        # plt.show()

        pre_S11 = calc_S11(pre_anneal_antenna, pre_anneal_dm)
        post_S11 = calc_S11(post_anneal_antenna, post_anneal_dm)
        pre_S11s.append(pre_S11)
        post_S11s.append(post_S11)

        frequencies = np.linspace(.6, 6, len(pre_S11), endpoint=True)

        # plt.plot(frequencies, 20*np.log10(np.abs(pre_S11)), label = "pre anneal")
        # plt.plot(frequencies, 20*np.log10(np.abs(post_S11)), label = "post anneal")
        # plt.title("Pre vs Post anneal antenna" + post_anneal_antenna_name)
        # plt.xlabel("Frequency (GHz)")
        # plt.ylabel("S11 (dB)")
        # plt.xlim([.5, 6])
        # plt.show()

    pre_mean = np.mean(20*np.log10(np.abs(pre_S11s)), axis=0)
    post_mean = np.mean(20*np.log10(np.abs(post_S11s)), axis=0)
    pre_std_dev = np.std(20*np.log10(np.abs(pre_S11s)), axis=0)
    post_std_dev = np.std(20*np.log10(np.abs(post_S11s)), axis=0)

    # pre_mean = 20*np.log10(np.mean(np.abs(pre_S11s), axis=0))
    # post_mean = 20*np.log10(np.mean(np.abs(post_S11s), axis=0))
    # pre_std_dev = 20*np.log10(np.std(np.abs(pre_S11s), axis=0))
    # post_std_dev= 20*np.log10(np.std(np.abs(post_S11s), axis=0))
  


    # plt.plot(frequencies, pre_mean, label='Mean')
    # plt.plot(frequencies, post_mean, label='Mean')
    # plt.show()

    return pre_mean, post_mean, pre_std_dev, post_std_dev

def main():
    pre_D3_mean, post_D3_mean, pre_D3_std_dev, post_D3_std_dev = avg('D3')
    pre_D4_mean, post_D4_mean, pre_D4_std_dev, post_D4_std_dev = avg('D4')
    pre_D5_mean, post_D5_mean, pre_D5_std_dev, post_D5_std_dev = avg('D5')

    pre_D3_std_dev =  [abs(pre_D3_std_dev[i]) if i%50 == 1 else 0 for i in range(len(pre_D3_std_dev))]
    post_D3_std_dev = [abs(post_D3_std_dev[i]) if i%50 == 6 else 0 for i in range(len(post_D3_std_dev))]
    post_D4_std_dev = [abs(post_D4_std_dev[i]) if i%50 == 11 else 0 for i in range(len(post_D4_std_dev))]
    post_D5_std_dev = [abs(post_D5_std_dev[i]) if i%50 == 16 else 0 for i in range(len(post_D5_std_dev))]

    frequencies = np.linspace(.6, 6, len(pre_D3_mean), endpoint=True)
    plt.errorbar(frequencies, pre_D3_mean, pre_D3_std_dev, label='pre anneal')
    plt.errorbar(frequencies, post_D3_mean, post_D3_std_dev,  label='D3 anneal (60s)')
    plt.errorbar(frequencies, post_D4_mean, post_D4_std_dev, label='D4 anneal (90s)')
    #plt.errorbar(frequencies, post_D5_mean, post_D5_std_dev, label='D5 anneal (30s)')
    plt.title("Average Annealed sample |S(1,1)|")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("|S(1,1)| dB")
    plt.legend()
    plt.show()

    plt.plot(frequencies, pre_D3_std_dev, label='pre anneal')
    plt.plot(frequencies, post_D3_std_dev, label='D3 anneal (60s)')
    plt.plot(frequencies, post_D4_std_dev, label='D4 anneal (90s)')
    plt.plot(frequencies, post_D5_std_dev, label='D5 anneal (30s)')
    plt.title("Standard Deviation Annealed sample Return Loss")
    plt.legend()
    plt.show()

    
    return

if __name__ == '__main__':
    main()