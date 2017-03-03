import os
import csv
import decimal
import math

directory_name = "/media/shtrikh17/Data/ZigBee/to_handle"
decimal.getcontext().prec = 6
NORMAL_NUMBER = 2

def make_feature_matrix(directory_name, feature_number, num_objects, start_object=0):
    """
    The function is used to parse multiple csv-files in order to create matrix with list of feature values.
     Returned values are to be used in Shannon's or Kullback's methods or in method of accumulated frequencies.

    :param directory_name: name of a directory to parse; it should contain CSV-files with the same feature set
    :param feature_number: number of feature to handle
    :param num_objects: amount of objects to take into account
    :param start_object: number of first object to take into account
    :return: list of class names (actually file names) and list with lists of feature values
    """

    def decimalize_matrix(feature_matrix):
        for column in feature_matrix:
            for i in range(len(column)):
                column[i] = decimal.Decimal(column[i])

    file_list = os.listdir(directory_name)
    feature_table = list()
    class_list = list()
    file_number = -1

    for filename in file_list:
        class_list.append(filename)
        feature_class = list()
        file_number += 1
        file = open(directory_name + "/" + filename, 'r')
        csv_reader = csv.reader(file, delimiter=';')
        current_object = 0
        for row in csv_reader:
            if current_object < start_object:
                current_object += 1
                continue
            feature_class.append(row[feature_number])
            current_object += 1
            if current_object >= num_objects:
                break
        feature_table.append(feature_class)
    decimalize_matrix(feature_table)
    return class_list, feature_table


def find_max_and_min(feature_matrix):
    """

    :param feature_matrix: list of lists with integers, which represent feature column
    :return: maximal and minimal elements in matrix
    """
    max_element = decimal.Decimal(feature_matrix[0][0])
    min_element = decimal.Decimal(feature_matrix[0][0])

    for column in feature_matrix:
        tmp = decimal.Decimal(max(column))
        if max_element < tmp:
            max_element = tmp
        tmp = decimal.Decimal(min(column))
        if min_element > tmp:
            min_element = tmp

    return max_element, min_element


def discretize_matrix(feature_matrix, maximum, minimum, amount):
    """
    This procedure converts matrix with continuous feature values into matrix with discrete values.
    :param feature_matrix: matrix to convert
    :param maximum: max value in matrix
    :param minimum: min value in matrix
    :param amount: number of segments
    :return: list of feature gradations
    """
    step = (maximum - minimum) / amount
    template = list()
    new_values = list()
    tmp = minimum

    if step == 0:
        new_values.append(maximum)
        return new_values

    while tmp <= maximum:
        template.append(tmp)
        tmp += step

    if len(template) == 1:
        new_values.append(template[0])
        return new_values
    for i in range(len(template)-1):
        new_values.append((template[i+1] + template[i]) / 2)

    def convert_element(element):
        for i in range(len(template)-1):
            if decimal.Decimal(element) >= template[i] and decimal.Decimal(element) < template[i+1]:
                return new_values[i]
        return new_values[len(new_values)-1]

    for lst in feature_matrix:
        for i in range(len(lst)):
            lst[i] = convert_element(lst[i])

    return new_values


def shannon_inform(feature_matrix, gradations_list):
    """
    Procedure to count shannon's information content.
    :param feature_matrix: list of lists with objects of different classes.
    :param gradations_list: list of gradations of feature
    :return: information content value
    """
    total_amount_of_objects = 0
    for column in feature_matrix:
        total_amount_of_objects += len(column)

    parts = list()

    for gradation in gradations_list:
        gradation_frequencies = list()
        for column in feature_matrix:
            m = 0
            for i in range(len(column)):
                if column[i] == gradation:
                    m += 1
            gradation_frequencies.append(m)

        total_gradation_amount = decimal.Decimal(0)
        for x in gradation_frequencies:
            total_gradation_amount += decimal.Decimal(x)

        parts_of_gradations_in_classes = list()

        for x in gradation_frequencies:
            if x > 0 and total_gradation_amount > 0:
                tmp = decimal.Decimal(x) / decimal.Decimal(total_gradation_amount)
            else:
                tmp = decimal.Decimal(0)
            parts_of_gradations_in_classes.append(tmp)

        part_of_gradation = total_gradation_amount / total_amount_of_objects

        part = 0

        for x in parts_of_gradations_in_classes:
            if x > 0:
                part += x * decimal.Decimal(math.log(x, len(feature_matrix)))

        part *= part_of_gradation
        parts.append(part)

    result = 0
    for x in parts:
        result += x
    result += 1

    return result


def shannon_pairs(feature_matrix, gradations_list, base_class=2):

    base_column = feature_matrix[base_class]
    result = list()


    for column in feature_matrix:
        if column is base_column:
            continue
        temp_matrix = list()
        temp_matrix.append(base_column)
        temp_matrix.append(column)
        res = shannon_inform(temp_matrix, gradations_list)
        result.append(res)

    return result


def write_csv(feature_matrix, filename):
    file = open(filename, "w")
    rows = list()
    for lst_num in range(len(feature_matrix)):
        if lst_num == 0:
            i = 0
            for x in feature_matrix[lst_num]:
                rows.append(list())
                rows[i].append(x)
                i += 1
        else:
            i = 0
            for i in range(len(feature_matrix[lst_num])):
                rows[i].append(feature_matrix[lst_num][i])
    writer = csv.writer(file, delimiter=';')

    for row in rows:
        writer.writerow(row)


def kullback_calculation(class_1, class_2, gradations_list):

    if len(gradations_list) == 1:
        return 0

    gradations_first = list()
    gradations_second = list()

    for gradation in gradations_list:
        freq_1 = 0
        freq_2 = 0
        for obj in class_1:
            if obj == gradation:
                freq_1 += 1
        for obj in class_2:
            if obj == gradation:
                freq_2 += 1
        gradations_first.append(freq_1)
        gradations_second.append(freq_2)

    sum_gradations_first = 0
    sum_gradations_second = 0
    for gradation in gradations_first:
        sum_gradations_first += gradation
    for gradation in gradations_second:
        sum_gradations_second += gradation

    for i in range(len(gradations_list)):
        gradations_first[i] = gradations_first[i] / sum_gradations_first
        gradations_second[i] = gradations_second[i] / sum_gradations_second

    result = 0
    for i in range(len(gradations_list)):
        if gradations_first[i] > 0 and gradations_second[i] > 0:
            tmp = gradations_first[i] / gradations_second[i]
            tmp = math.log(tmp, 2)
            tmp = tmp * (gradations_first[i] - gradations_second[i])
            result += tmp

    return result


def kullback_inform(feature_matrix, gradations_list, base_class):
    base_class_column = feature_matrix[base_class]

    result = list()

    for column in feature_matrix:
        if column is base_class_column:
            continue
        inform_content = kullback_calculation(base_class_column, column, gradations_list)
        result.append(inform_content)

    return result


def accum_calc(class_1, class_2, gradations_list):

    gradations_first = list()
    gradations_second = list()

    for i in range(len(gradations_list)):
        tmp = 0
        for x in class_1:
            if x == gradations_list[i]:
                tmp += 1
        gradations_first.append(tmp)
        tmp = 0
        for x in class_2:
            if x == gradations_list[i]:
                tmp += 1
        gradations_second.append(tmp)

    acc_freq_1 = list()
    acc_freq_2 = list()

    for i in range(len(gradations_list)):
        if i == 0:
            acc_freq_1.append(gradations_first[i])
            acc_freq_2.append(gradations_second[i])
        else:
            acc_freq_1.append(acc_freq_1[len(acc_freq_1)-1]+gradations_first[i])
            acc_freq_2.append(acc_freq_2[len(acc_freq_2) - 1] + gradations_second[i])

    max_diff = 0
    for i in range(len(gradations_list)):
        tmp = abs(acc_freq_1[i] - acc_freq_2[i])
        if tmp > max_diff:
            max_diff = tmp

    return max_diff


def accumulated_frequencies(feature_matrix, gradations_list, base_class):
    base_class_column = feature_matrix[base_class]

    result = list()
    for column in feature_matrix:
        if column is base_class_column:
            continue
        res = accum_calc(base_class_column, column, gradations_list)
        result.append(res)

    return result


def run_all(directory_name, num_features, num_objects, first_object=0):
    shannon_result = list()
    shannon_pairs_result = list()
    kullback_result = list()
    accum_result = list()
    for feature in range(num_features):
        print("Feature: " + str(feature+1))
        class_list, feature_table = make_feature_matrix(directory_name, feature, num_objects, first_object)
        maximum, minimum = find_max_and_min(feature_table)
        gradations = discretize_matrix(feature_table, decimal.Decimal(maximum), decimal.Decimal(minimum), 10)
        shannon = shannon_inform(feature_table, gradations)
        shannon_result.append(shannon)
        print(shannon)
        shannon_couples = shannon_pairs(feature_table, gradations, NORMAL_NUMBER)
        shannon_pairs_result.append(shannon_couples)
        print(shannon_couples)
        kullback = kullback_inform(feature_table, gradations, 2)
        kullback_result.append(kullback)
        print(kullback)
        accum = accumulated_frequencies(feature_table, gradations, 2)
        accum_result.append(accum)
        print(accum)
    return class_list, shannon_result, shannon_pairs_result, kullback_result, accum_result


def make_report(directory_name, class_list, num_features, results_shannon, results_shannon_pairs, results_kullback, results_accum):
    report_file = open("/media/shtrikh17/Data/ZigBee/report.txt", "w")
    output_file_shannon = open("/media/shtrikh17/Data/ZigBee/result_shannon.csv", "w")
    output_file_shannon_pairs = open("/media/shtrikh17/Data/ZigBee/result_shannon_pairs.csv", "w")
    output_file_kullback = open("/media/shtrikh17/Data/ZigBee/result_kullback.csv", "w")
    output_file_accum = open("/media/shtrikh17/Data/ZigBee/result_accum.csv", "w")
    report_file.write("Report on parse of:\t" + directory_name + "\n\n")
    report_file.write("Classes: \n")
    for x in class_list:
        report_file.write("{0}: ".format(class_list.index(x)))
        report_file.write(x + "\n")
    report_file.write("\n" + "=" * 50 + "\n")
    report_file.write("\n")

    for i in range(num_features):
        report_file.write("Report for feature #" + str(i+1) + ":\n")
        report_file.write("\n")
        report_file.write("Shannon's information content:\t" + str(results_shannon[i]) + "\n")
        report_file.write("\n")

        report_file.write("Shannon's information content for pairs:\n")
        k = 0
        for j in range(len(results_shannon_pairs[i])):
            if j == NORMAL_NUMBER:
                k += 1
            report_file.write("Class #{0}: ".format(k) + str(results_shannon_pairs[i][j]) + "\n")
            k += 1
        report_file.write("\n")

        report_file.write("Kullback's information content:\n")
        k = 0
        for j in range(len(results_kullback[i])):
            if j == NORMAL_NUMBER:
                k += 1
            report_file.write("Class #{0}: ".format(k) + str(results_kullback[i][j]) + "\n")
            k += 1
        report_file.write("\n")

        report_file.write("Accumulated frequencies information content:\n")
        k = 0
        for j in range(len(results_accum[i])):
            if j == NORMAL_NUMBER:
                k += 1
            report_file.write("Class #{0}: ".format(k) + str(results_accum[i][j]) + "\n")
            k += 1
        report_file.write("\n")

        report_file.write("=" * 50 + "\n")
        report_file.write("\n")

    #=================================

    shannon_writer = csv.writer(output_file_shannon, delimiter=";")
    shannon_writer.writerow(results_shannon)

    shannon_pairs_writer = csv.writer(output_file_shannon_pairs, delimiter=";")

    kullback_writer = csv.writer(output_file_kullback, delimiter=";")

    heading = list()
    k = 0
    for i in range(len(results_kullback[0])):
        if i == NORMAL_NUMBER:
            k += 1
        heading.append("Class #{0}".format(k))
        k += 1

    shannon_pairs_writer.writerow(heading)
    for row in results_shannon_pairs:
        shannon_pairs_writer.writerow(row)

    kullback_writer.writerow(heading)
    for row in results_kullback:
        kullback_writer.writerow(row)

    accum_writer = csv.writer(output_file_accum, delimiter=";")
    accum_writer.writerow(heading)
    for row in results_accum:
        accum_writer.writerow(row)


#=========================

class_list, shannon, pairs_shannon, kullback, accum = run_all(directory_name, 51, 800)
make_report(directory_name, class_list, 51, shannon, pairs_shannon, kullback, accum)
