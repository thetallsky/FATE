#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#


from federatedml.protobuf.generated import sir_meta_pb2, sir_param_pb2
from federatedml.model_base import Metric, MetricMeta
from federatedml.model_base import ModelBase
from federatedml.param.sir_param import SecureInformationRetrievalParam
from federatedml.statistic.intersect.match_id_process import MatchIDIntersect
from federatedml.util import consts, abnormal_detection
from federatedml.transfer_variable.transfer_class.secure_information_retrieval_transfer_variable import \
    SecureInformationRetrievalTransferVariable


MODEL_PARAM_NAME = 'SecureInformationRetrievalParam'
MODEL_META_NAME = 'SecureInformationRetrievalMeta'


class BaseSecureInformationRetrieval(ModelBase):
    """

    """
    def __init__(self):
        super(BaseSecureInformationRetrieval, self).__init__()
        self.model_param = SecureInformationRetrievalParam()
        self.security_level = None
        self.commutative_cipher = None
        self.transfer_variable = None
        self.block_num = None       # N in 1-N OT
        self.coverage = None        # the percentage of transactions whose values are successfully retrieved

        self.dh_params = None
        self.intersection_obj = None
        self.proc_obj = None
        self.with_inst_id = None
        self.need_label = False
        self.target_cols = None

        # For callback
        self.metric_name = "sir"
        self.metric_namespace = "train"
        self.metric_type = "SIR"

    def _init_base_model(self, param: SecureInformationRetrievalParam):
        self.transfer_variable = SecureInformationRetrievalTransferVariable()
        self._init_transfer_variable()

        self.model_param = param
        self.security_level = self.model_param.security_level
        self.dh_params = self.model_param.dh_params
        self.target_cols = self.model_param.target_cols

    def _init_transfer_variable(self):
        self.transfer_variable.natural_indexation.disable_auto_clean()
        self.transfer_variable.id_blocks_ciphertext.disable_auto_clean()

    @staticmethod
    def _abnormal_detection(data_instances):
        """
        Make sure input data_instances is valid.
        """
        abnormal_detection.empty_table_detection(data_instances)
        abnormal_detection.empty_feature_detection(data_instances)

    """    
    @staticmethod
    def record_original_id(k, v):
        if isinstance(k, str):
            restored_id = conversion.int_to_str(conversion.str_to_int(k))
        else:
            restored_id = k
        return (restored_id, k)
    """

    def _check_need_label(self):
        return len(self.target_cols) == 0

    def _recover_match_id(self, data_instance):
        self.proc_obj = MatchIDIntersect(sample_id_generator=consts.GUEST, role=self.intersection_obj.role)
        self.proc_obj.new_join_id = False
        self.proc_obj.use_sample_id()
        match_data = self.proc_obj.recover(data=data_instance)
        return match_data

    def _restore_sample_id(self, data_instances):
        restore_data = self.proc_obj.expand(data_instances, owner_only=True)

        return restore_data

    def _raw_information_retrieval(self, data_instance):
        """
        If security_level == 0, then perform raw information retrieval
        :param data_instance:
        :return:
        """
        pass

    def _parse_security_level(self, data_instance):
        """
        Cooperatively parse the security level index
        :param data_instance:
        :return:
        """
        pass

    def _sync_natural_index(self, id_list_arr):
        """
        guest -> host
        :param id_list_arr:
        :return:
        """

    def _sync_natural_indexation(self, id_list, time):
        """
        guest -> host
        :param id_list:
        :param time
        :return:
        """

    def _sync_block_num(self):
        """
        guest -> host
        :param
        :return:
        """

    def _transmit_value_ciphertext(self, id_block, time):
        """
        host -> guest
        :param id_block:
        :param time: int
        :return:
        """

    def _check_oblivious_transfer_condition(self):
        """
        1-N OT with N no smaller than 2 is supported
        :return:
        """
        return self.block_num >= 2

    def _failure_response(self):
        """
        If even 1-2 OT cannot be performed, make failure response
        :return:
        """
        raise ValueError("Cannot perform even 1-2 OT, recommend use raw retrieval")

    def _sync_coverage(self, data_instance):
        """
        guest -> host
        :param data_instance:
        :return:
        """
        pass

    def _sync_nonce_list(self, nonce, time):
        """
        host -> guest
        :param nonce:
        :return:
        """
        pass

    def export_model(self):
        if self.model_output is not None:
            return self.model_output

        meta_obj = self._get_meta()
        param_obj = self._get_param()
        result = {
            MODEL_META_NAME: meta_obj,
            MODEL_PARAM_NAME: param_obj
        }
        self.model_output = result
        return result

    def _get_meta(self):
        return sir_meta_pb2.SecureInformationRetrievalMeta(
            security_level=self.security_level,
            oblivious_transfer_protocol=self.model_param.oblivious_transfer_protocol,
            commutative_encryption=self.model_param.commutative_encryption,
            non_committing_encryption=self.model_param.non_committing_encryption,
            key_size=self.model_param.key_size,
            raw_retrieval=self.model_param.raw_retrieval
        )

    def _get_param(self):
        return sir_param_pb2.SecureInformationRetrievalParam(
            coverage=self.coverage,
            block_num=self.block_num
        )

    def _display_result(self, block_num=None):
        if block_num is None:
            self.callback_metric(metric_name=self.metric_name,
                                 metric_namespace=self.metric_namespace,
                                 metric_data=[Metric("Coverage", self.coverage),
                                              Metric("Block number", self.block_num)])
            self.tracker.set_metric_meta(metric_namespace=self.metric_namespace,
                                         metric_name=self.metric_name,
                                         metric_meta=MetricMeta(self.metric_name, metric_type="INTERSECTION"))
        else:
            self.callback_metric(metric_name=self.metric_name,
                                 metric_namespace=self.metric_namespace,
                                 metric_data=[Metric("Coverage", self.coverage),
                                              Metric("Block number", block_num)])
            self.tracker.set_metric_meta(metric_namespace=self.metric_namespace,
                                         metric_name=self.metric_name,
                                         metric_meta=MetricMeta(self.metric_name, metric_type="INTERSECTION"))

    """
    @staticmethod
    def _set_schema(data_instance, id_name=None, label_name=None, feature_name=None):
    
        if id_name is not None:
            data_instance.schema['sid_name'] = id_name
        if label_name is not None:
            data_instance.schema['label_name'] = label_name
        if feature_name is not None:
            data_instance.schema['header'] = feature_name
        return data_instance

    @staticmethod
    def log_table(tab, mode=0):
        # tab_col = tab.collect()
        if mode == 0:
            LOGGER.debug("mode 0: k, v")
        elif mode == 1:
            LOGGER.debug("mode 1: k, v.label")
        elif mode == 2:
            LOGGER.debug("mode 2: k, v.id, v.label")
        elif mode == 3:
           LOGGER.debug("mode 3: k, v.id, v.features, v.label")

    @staticmethod
    def log_schema(tab):
        
        LOGGER.debug("tab schema = {}".format(tab.schema))
    """
