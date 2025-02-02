import pandas as pd
import matplotlib.pyplot as plt

# 读取 CSV 文件
global_data = pd.read_csv('../planner-benchmark.csv')

topology_list = ['cycle', 'chain', 'star', 'clique']
target_list = ['cost', 'time']

# current option
# topology_list = ['cycle', 'chain']
# topology_list = ['star', 'clique']
# target_list = ['time'] # Time is what we concered most
# target_list = ['cost']

focus_method = [
                "DPccp",
                # "IKKBZ",
                "GOO",
                # "BU-hanwen-layered-zero",
                # "BU-hanwen-layered2-zero",
                # "BU-hanwen-layered3-zero",
                # "BU-hanwen-layered-sorted1-zero",
                # "BU-hanwen-layered-sorted2-zero",
                "BU-hanwen-layered-sorted3-zero"
                # "BU-hanwen-layered-sorted4-zero",
                # "BU-hanwen-layered-sorted5-zero",
                # "BU-hanwen-layered-sorted6-zero",
                "BU-hanwen-layered-sorted-dynamic2-zero",
    "BU-hanwen-layered-sorted-dynamic3-zero",
                "TD-hanwen-layered3-zero",
                "TD-hanwen-layered3-sum",
                # 'BU-A*-zero', "TD-A*-sum",
                # "BU-beam-zero",
                # "TD-beam-zero",
                # "BU-beam-hanwen-zero",
                # "TD-beam-hanwen-zero",a
                # "BU-BIDIRECTIONAL-zero",
                # "BU-LAYEREDBIDIRECTIONAL-zero"
                ]

for topology in topology_list:
    for target in target_list:
        fig, ax = plt.subplots(figsize=(30, 12))
        data = global_data[global_data['topology'] == topology]

        for method in focus_method:
            sub_data = data[(data['planner'] == method) & (data['cost'].notnull()) & (data['time'] <= 50)]
            marker = 'x' if method not in ["DPccp", "BU-BIDIRECTIONAL-zero"] else 'o'

            if "sorted" in method: marker = '^'
            if "TD" in method:marker = 'o'
            ax.plot(sub_data['size'], sub_data[target], marker=marker, label='{}'.format(method))
            for i in range(len(sub_data)):
                ax.text(sub_data['size'].iloc[i], sub_data[target].iloc[i], str(sub_data[target].iloc[i]),
                        ha='center', va='bottom')

        # 设置图的标题和坐标轴标签
        ax.set_title('Comparison of {} {}'.format(target, focus_method))
        ax.set_xlabel('#relations')
        ax.set_ylabel('Opt. time' if target == 'time' else 'cost')

        # 设置图例
        ax.legend()

        # 显示图
        plt.savefig('comparison_{}_{}.png'.format(target, topology))

# valids = ["BU-LAYEREDBIDIRECTIONAL-zero", "BU-BIDIRECTIONAL-zero"]
# valids = ["BU-hanwen-layered-zero"]
#
# for topology in topology_list:
#     for valid_method in valids:
#         valid_num = len(global_data[(global_data['topology'] == topology) & (global_data['planner'] == valid_method) &
#                                     global_data['cost'] != 0])
#         valid_total_num = len(
#             global_data[(global_data['topology'] == topology) & (global_data['planner'] == valid_method)])
#         valid_rate = valid_num / valid_total_num if valid_total_num != 0 else 0
#         print(
#             "{} {} valid_rate is {}% = {} / {}".format(valid_method, topology, valid_rate*100, valid_num, valid_total_num))
#     print()