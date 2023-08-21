import csv


def detect_dy_in_addresses(data):
    # 朝代名从 belongsX_Name 的最后一个获得
    # 需要找到最后一个有内容的 belongsX_Name
    # 并且这个内容中含有“朝”。在输出的时候，“朝”
    # 需要被删除。
    output = ""
    data_reversed = list(reversed(data))
    for i in range(len(data_reversed)):
        cell = data[i]
        if cell!="" and "朝" in cell[-1]:
            output = cell[:-1]
            return output


class FileOperation:
    @staticmethod
    def read_addresses(file_name):
        # output_dic 的数据结构是：以朝代名中文作为 index，value
        # 是 addresses 中的一个 row
        output_dic = {}
        with open(file_name, "r", encoding="utf-8") as f:
            csv_reader = csv.reader(f, delimiter="\t")
            for row in csv_reader:
                dy = detect_dy_in_addresses(row)
                if dy not in output_dic:
                    output_dic[dy] = [row]
                else:
                    output_dic[dy].append(row)
        return output_dic

    @staticmethod
    def read_input(file_name):
        output = []
        with open(file_name, "r", encoding="utf-8") as f:
            csv_reader = csv.reader(f, delimiter="\t")
            for row in csv_reader:
                output.append(row)
        return output

    @staticmethod
    def write_data(file_name, data_list_coded):
        output = ""
        for i in data_list_coded:
            output += "\t".join(i) + "\n"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(output)

def code_data(data_list, addr_dic):
    output = []
    for line in data_list:
        cbdb_addr_id = "unknown"
        addr_id = line[0]
        addr_dy = line[1]
        addr_name = line[2]
        if addr_dy in addr_dic:
            for addresses_item in addr_dic[addr_dy]:
                addresses_item_name_chn = addresses_item[3]
                addresses_item_name_id = addresses_item[0]
                if addresses_item_name_chn == addr_name:
                    cbdb_addr_id = addresses_item_name_id
                    break
        output.append([addr_id, addr_dy, addr_name, cbdb_addr_id])
    return output


# 未來可以嘗試實現：
# 1，帶上允許時間限制的條件；
#
# 2，如果有多項匹配，優先選擇有坐標信息的。
# （當前可以透過工程來實現這一點：把 ADDRESSES 按照 id 和 坐標（坐標由大到小）排序。坐標有值的排在前面


read_file_class = FileOperation()
addr_dic = FileOperation.read_addresses("ADDRESSES.txt")
data_list = FileOperation.read_input("input.txt")
data_list_coded = code_data(data_list, addr_dic)
FileOperation.write_data("output.txt", data_list_coded)
print("done")
