import csv

# define ADDRESSES table index
cbdb_addr_id_index = 0
cbdb_addr_name_index = 3
cbdb_addr_fy_index = 5
cbdb_addr_ly_index = 6
cbdb_addr_x_index = 7
cbdb_addr_y_index = 8


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

def add_belong_name_list_to_addresses_list(row, capture_belongs_index_list):
    output = []
    belongs_list = []
    for i_index, i_value in enumerate(row):
        if i_index in capture_belongs_index_list:
            belongs_list.append(i_value)
        output.append(output+belongs_list)
    output = row + [belongs_list]
    return output

class FileOperation:
    @staticmethod
    def read_addresses(file_name):
        # output_dic 的数据结构是：以朝代名中文作为 index，value
        # 是 addresses 中的一个 row
        output_dic = {}
        capture_belongs_str = "belongs"
        capture_chn_str = "chn"
        capture_stop_number_str = "_ID"
        capture_belongs_index_list = []
        with open(file_name, "r", encoding="utf-8") as f:
            csv_reader = csv.reader(f, delimiter="\t")
            counter = 1
            for row in csv_reader:
                # skip 只有一个字的地址名，以及 skip 地址名为空的记录
                if len(row[cbdb_addr_id_index]) <=1:
                    continue
                if counter == 1:
                    for index, value in enumerate(row):
                        if (capture_belongs_str in value) and (capture_chn_str in value) and (capture_stop_number_str not in value) and value!="":
                            capture_belongs_index_list.append(index)
                counter+=1
                dy = detect_dy_in_addresses(row)
                row = add_belong_name_list_to_addresses_list(row, capture_belongs_index_list)
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

def match_belongs_info(addr_list, addr_name):
    if addr_name in addr_list:
        return addr_name
    for addr_in_addrlist in addr_list:
        if addr_in_addrlist in addr_name or addr_name in addr_in_addrlist:
            return addr_in_addrlist
    return ""

def code_data(data_list, addr_dic):
    output = []
    for line in data_list:
        addr_id = line[0]
        addr_dy = line[1]
        addr_name = line[2]
        addr_belong = line[3]
        addr_time = line[4]
        exact_with_belong_match_list = []
        partial_with_belong_match_list = []
        excat_without_belong_match_list = []
        partial_without_belong_match_list = []
        if addr_dy in addr_dic:
            for addresses_item in sorted(addr_dic[addr_dy], key=lambda x: (-len(x[cbdb_addr_name_index]), -len(x[cbdb_addr_x_index]))):
                addresses_item_name_chn = addresses_item[cbdb_addr_name_index]
                addresses_item_name_id = addresses_item[cbdb_addr_id_index]
                addresses_addr_id = addresses_item_name_id
                addresses_item_belong_list = addresses_item[-1]
                addresses_fy = addresses_item[cbdb_addr_fy_index]
                addresses_ly = addresses_item[cbdb_addr_ly_index]
                matched_term = ""
                matched_time = 0
                # match time information by first and last years
                if addresses_fy != 0 and addresses_ly != 0 and addresses_ly != "" and addresses_ly !="" and addr_time != 0 and addr_time != "":
                    if addr_time >= addresses_fy and addr_time <= addresses_ly:
                        matched_time = 1
                # give a pass token to the reocrds which don't have time information. 不進行時間匹配時，input 最後一列留空即可
                if addr_time == "":
                    matched_time = 1
                # if addresses_item_name_chn in addr_name:
                if (addr_name in addresses_item_name_chn or addresses_item_name_chn in addr_name) and (matched_time == 1):
                    matched_term = match_belongs_info(addresses_item_belong_list, addr_belong)
                    if addr_name == addresses_item_name_chn and matched_term != "":
                        exact_with_belong_match_list.append([addresses_addr_id, "exact_with_belong", addresses_item_name_chn, matched_term])
                    elif addr_name != addresses_item_name_chn and matched_term != "":
                        partial_with_belong_match_list.append([addresses_addr_id, "partial_with_belong", addresses_item_name_chn, matched_term])
                    elif addr_name == addresses_item_name_chn and matched_term == "":
                        excat_without_belong_match_list.append([addresses_addr_id, "excat_without_belong", addresses_item_name_chn, matched_term])
                    else:
                        partial_without_belong_match_list.append([addresses_addr_id, "partial_without_belong", addresses_item_name_chn, matched_term]) 
        if len(exact_with_belong_match_list) > 0:
            output.append([addr_id, addr_dy, addr_name, addr_belong, addr_time] + exact_with_belong_match_list[0])
        elif len(partial_with_belong_match_list) > 0:
            output.append([addr_id, addr_dy, addr_name, addr_belong, addr_time] + partial_with_belong_match_list[0])
        elif len(excat_without_belong_match_list) > 0:
            output.append([addr_id, addr_dy, addr_name, addr_belong, addr_time] + excat_without_belong_match_list[0])
        elif len(partial_without_belong_match_list) > 0:
            output.append([addr_id, addr_dy, addr_name, addr_belong, addr_time] + partial_without_belong_match_list[0])
        else:
            output.append([addr_id, addr_dy, addr_name, addr_belong, addr_time, "", "unknown", "", ""])
    return output

# Input Schema
# id	dy	addr_name	addr_belong	time
# 1	宋	甌寧	建州	1279

read_file_class = FileOperation()
addr_dic = FileOperation.read_addresses("ADDRESSES.txt")
data_list = FileOperation.read_input("input.txt")
addr_type_list = FileOperation.read_input("cbdb_entity_address_types.csv")
addr_type_list = [i[0] for i in addr_type_list[1:]]
print(addr_type_list)

raise
data_list_coded = code_data(data_list, addr_dic)
FileOperation.write_data("output.txt", data_list_coded)
print("done")
