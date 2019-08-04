import collections as col
import numpy as np


class Torch2TF:
    @classmethod
    def convert_conv(cls, w):
        # [C_out, C_in, H, W] => [H, W, C_in, C_out]
        return np.moveaxis(w, [0, 1, 2, 3], [3, 2, 0, 1])

    @classmethod
    def convert_fc_weight(cls, w):
        return w.swapaxes(0, 1)


class TF2Torch:
    @classmethod
    def convert_conv(cls, w):
        # [H, W, C_in, C_out] => [C_out, C_in, H, W]
        return np.moveaxis(w, [0, 1, 2, 3], [2, 3, 1, 0])

    @classmethod
    def convert_fc_weight(cls, w):
        return w.swapaxes(0, 1)


def export_tf_weights(session):
    import tensorflow as tf

    param_variables = session.graph.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)

    # Batch norm variables aren't trainable
    bn_running_variables = []
    for variable in session.graph.get_collection(tf.GraphKeys.GLOBAL_VARIABLES):
        if "batch_normalization" in variable.name \
                and "moving" in variable.name:
            bn_running_variables.append(variable)

    all_variables = param_variables + bn_running_variables

    all_variables_dict = col.OrderedDict([
        (var.name, var)
        for var in all_variables
    ])
    variable_values_dict = session.run(all_variables_dict)
    return variable_values_dict
