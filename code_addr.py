"""
给朝代的地名加地名id

思路：
1. 根据地名表ADDRESSES.txt，生成addr_dic[朝代名]=地名列表（按地名长度倒序）
2. 根据地名类型表cbdb_entity_address_types.csv，生成addr_type_list[]一维数组
3. 地名匹配，加地名id：根据group_keywords、addr_dic、addr_type_list，
将input.txt中的地名加上地名id、匹配类型，输出为output.txt

地名匹配规则：
1. 按优先级group_keywords顺序匹配
2. 按addr_dic从右往左匹配
3. 对于在规则2中没有匹配到的，从右往左按addr_type_list进行分隔，然后再按规则2匹配

注意：
ADDRESSES.txt中朝代一般在最后一列，但在哪一列不确定，因为地名层级不同

"""

import csv
import copy
import re

# define ADDRESSES table index
cbdb_addr_id_index = 0  # 地名id
cbdb_addr_name_index = 3  # 地名
cbdb_addr_fy_index = 5  # 地名开始时间，first year
cbdb_addr_ly_index = 6  # 地名结束时间，last year
cbdb_addr_x_index = 7  # 地名纬度
cbdb_addr_y_index = 8  # 地名经度


def detect_dy_in_addresses(data):
    # 朝代名从 belongsX_Name 的最后一个获得
    # 需要找到最后一个有内容的 belongsX_Name
    # 并且这个内容中含有“朝”。在输出的时候，“朝”
    # 需要被删除。
    output = ""
    data_reversed = list(reversed(data))
    for i in range(len(data_reversed)):
        cell = data[i]
        if cell != "" and "朝" in cell[-1]:
            output = cell[:-1]
            return output


def add_belong_name_list_to_addresses_list(row, capture_belongs_index_list):
    output = []
    belongs_list = []
    for i_index, i_value in enumerate(row):
        if i_index in capture_belongs_index_list:
            belongs_list.append(i_value)
        output.append(output + belongs_list)
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
                if len(row[cbdb_addr_id_index]) <= 1:
                    continue
                if counter == 1:
                    for index, value in enumerate(row):
                        if (capture_belongs_str in value) and (capture_chn_str in value) and (
                                capture_stop_number_str not in value) and value != "":
                            capture_belongs_index_list.append(index)
                counter += 1
                dy = detect_dy_in_addresses(row)
                row = add_belong_name_list_to_addresses_list(row, capture_belongs_index_list)
                if dy not in output_dic:
                    output_dic[dy] = [row]
                else:
                    output_dic[dy].append(row)
        # 排序 add xiujunhan 2023-08-29
        for dy, row in output_dic.items():
            output_dic[dy] = sorted(output_dic[dy],
                                    key=lambda x: (-len(x[cbdb_addr_name_index]), -len(x[cbdb_addr_x_index])))

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


def rstrip_word(string, word):
    return re.sub(f'{word}$', '', string)


def code_data(data_list, addr_dic, current_group_keywords, group_keywords, addr_type_list):
    output = []
    counter = 0
    data_list_len = len(data_list)
    group_keywords_for_code_data = copy.deepcopy(group_keywords)
    group_keywords_for_code_data.remove(current_group_keywords)
    for line in data_list:
        addr_id = line[0]
        addr_dy = line[1]
        addr_name = line[2]
        addr_belong = line[3]
        addr_time = line[4]
        if addr_time == "no_info": addr_time = ""
        exact_with_belong_match_list = []
        partial_with_belong_match_list = []
        excat_without_belong_match_list = []
        partial_without_belong_match_list = []
        counter += 1
        if counter % 10 == 0:
            print(str(counter) + "/" + str(data_list_len) + " done.")
        if addr_dy in addr_dic:
            for addresses_item in addr_dic[addr_dy]:
                addresses_item_name_chn = addresses_item[cbdb_addr_name_index]
                addresses_item_name_id = addresses_item[cbdb_addr_id_index]
                addresses_addr_id = addresses_item_name_id
                addresses_item_belong_list = addresses_item[-1]
                addresses_fy = addresses_item[cbdb_addr_fy_index]
                addresses_ly = addresses_item[cbdb_addr_ly_index]
                matched_term = ""
                matched_time = 0
                break_token = 0
                if current_group_keywords == "None":
                    for keyword in group_keywords_for_code_data:
                        if len(addresses_item_name_chn) >= len(keyword):
                            if addresses_item_name_chn[-len(keyword):] == keyword:
                                break_token = 1
                                break
                        if len(addr_name) >= len(keyword):
                            if addr_name[-len(keyword):] == keyword:
                                break_token = 1
                                break
                else:
                    if len(addresses_item_name_chn) >= len(current_group_keywords):
                        if addresses_item_name_chn[-len(current_group_keywords):] != current_group_keywords:
                            break_token = 1
                if break_token == 1:
                    continue
                # match time information by first and last years
                if addresses_fy != 0 and addresses_ly != 0 and addresses_ly != "" and addresses_ly != "" and addr_time != 0 and addr_time != "":
                    if addr_time >= addresses_fy and addr_time <= addresses_ly:
                        matched_time = 1
                # give a pass token to the reocrds which don't have time information. 不進行時間匹配時，input 最後一列留空即可
                if addr_time == "":
                    matched_time = 1
                # if addresses_item_name_chn in addr_name:
                if (addr_name in addresses_item_name_chn or addresses_item_name_chn in addr_name) and (
                        matched_time == 1):
                    matched_term = match_belongs_info(addresses_item_belong_list, addr_belong)
                    if addr_name == addresses_item_name_chn and matched_term != "":
                        exact_with_belong_match_list.append(
                            [addresses_addr_id, "exact_with_belong", addresses_item_name_chn, matched_term])
                    elif addr_name != addresses_item_name_chn and matched_term != "" and (
                            addr_name.find(addresses_item_name_chn) == 1 or addresses_item_name_chn.find(
                        addr_name) == 1):
                        partial_with_belong_match_list.append(
                            [addresses_addr_id, "partial_with_belong_dangerous", addresses_item_name_chn, matched_term])
                    elif addr_name != addresses_item_name_chn and matched_term != "":
                        partial_with_belong_match_list.append(
                            [addresses_addr_id, "partial_with_belong", addresses_item_name_chn, matched_term])
                    elif addr_name == addresses_item_name_chn and matched_term == "":
                        excat_without_belong_match_list.append(
                            [addresses_addr_id, "excat_without_belong", addresses_item_name_chn, matched_term])
                    elif addr_name.find(addresses_item_name_chn) == 1 or addresses_item_name_chn.find(addr_name) == 1:
                        partial_without_belong_match_list.append(
                            [addresses_addr_id, "partial_without_belong_dangerous", addresses_item_name_chn,
                             matched_term])
                    else:
                        partial_without_belong_match_list.append(
                            [addresses_addr_id, "partial_without_belong", addresses_item_name_chn, matched_term])
                        # remove the type the address name and try to match again
                else:
                    for addr_type in addr_type_list:
                        addr_name_short = rstrip_word(addr_name, addr_type)
                        addresses_item_name_chn_short = rstrip_word(addresses_item_name_chn, addr_type)
                        if len(addr_name_short) <= 1:
                            continue
                        if len(addresses_item_name_chn_short) <= 1:
                            continue
                        if (
                                addr_name_short in addresses_item_name_chn_short or addresses_item_name_chn_short in addr_name_short) and (
                                matched_time == 1):
                            matched_term = match_belongs_info(addresses_item_belong_list, addr_belong)
                            if matched_term != "" and (addr_name_short.find(
                                    addresses_item_name_chn_short) == 1 or addresses_item_name_chn_short.find(
                                addr_name_short) == 1):
                                partial_with_belong_match_list.append(
                                    [addresses_addr_id, "partial_with_belong_dangerous", addresses_item_name_chn,
                                     matched_term])
                            elif matched_term != "":
                                partial_with_belong_match_list.append(
                                    [addresses_addr_id, "partial_with_belong", addresses_item_name_chn, matched_term])
                            elif addr_name_short.find(
                                    addresses_item_name_chn_short) == 1 or addresses_item_name_chn_short.find(
                                addr_name_short) == 1:
                                partial_without_belong_match_list.append(
                                    [addresses_addr_id, "partial_without_belong_dangerous", addresses_item_name_chn,
                                     matched_term])
                            else:
                                partial_without_belong_match_list.append(
                                    [addresses_addr_id, "partial_without_belong", addresses_item_name_chn,
                                     matched_term])
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


def create_input_groups(data_list, group_keywords):
    output = []
    residual_list = copy.deepcopy(data_list)
    none_location = group_keywords.index("None")
    group_keywords_without_none = copy.deepcopy(group_keywords)
    group_keywords_without_none.remove("None")
    for keyword in group_keywords_without_none:
        current_keyword_list = []
        for line in list(residual_list):
            addr_name = line[2]
            if addr_name[-len(keyword):] == keyword:
                current_keyword_list.append(line)
                residual_list.remove(line)
        output.append(current_keyword_list)
    output[none_location:none_location] = [residual_list]
    return output


def merge_coded_groups(data_list_coded, data_list_coded_groups):
    data_list_coded_groups = data_list_coded_groups[1:]
    for data_list_coded_group in data_list_coded_groups:
        for line_idx in range(len(data_list_coded_group)):
            if data_list_coded[line_idx][6] == "unknown" and data_list_coded_group[line_idx][5] != "unknown":
                data_list_coded[line_idx] = data_list_coded_group[line_idx]
    return data_list_coded


# Input Schema
# id	dy	addr_name	addr_belong	time
# 1	宋	甌寧	建州	1279
# 2	清	江南太平府	no_info	no_info

read_file_class = FileOperation()
addr_dic = FileOperation.read_addresses("ADDRESSES.txt")
# data_list = FileOperation.read_input("input.txt")
data_list = FileOperation.read_input("input_small.txt")    # test
group_keywords = ["None", "衛"]
group_list = create_input_groups(data_list, group_keywords)
addr_type_list = FileOperation.read_input("cbdb_entity_address_types.csv")
addr_type_list = [i[0] for i in addr_type_list[1:]]
data_list_coded_groups = []
for group_idx in range(len(group_keywords)):
    current_group_keywords = group_keywords[group_idx]
    print("group " + current_group_keywords + " is processing")
    data_list_coded_groups.append(
        code_data(data_list, addr_dic, current_group_keywords, group_keywords, addr_type_list))
data_list_coded = copy.deepcopy(data_list_coded_groups[0])
if len(data_list_coded_groups) > 1:
    data_list_coded = merge_coded_groups(data_list_coded, data_list_coded_groups)
# FileOperation.write_data("output.txt", data_list_coded)
FileOperation.write_data("output2.txt", data_list_coded)    # test
print("done")
