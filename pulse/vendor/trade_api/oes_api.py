# -*- coding: utf-8 -*-
"""
oes capi的python封装
"""

import time
import errno

from collections import OrderedDict
from typing import Any, Dict, List, Optional

from ctypes import (
    c_char, c_int64, Array, byref, POINTER, _Pointer, pointer,
    create_string_buffer
)

from vendor.trade_api.model import (
    # spk_util.py
    VOID_NULLPTR, CHAR_NULLPTR,
    GENERAL_CLI_MAX_NAME_LEN,
    GENERAL_CLI_MAX_REMOTE_CNT,
    SPK_ENDPOINT_MAX_REMOTE_CNT,
    spk_decorator_exception,
    SMsgHeadT, OesApiRemoteCfgT, OesApiAddrInfoT, OesAsyncApiChannelCfgT,
    OesAsyncApiChannelT, UnionForUserInfo,

    # oes_base_constants.py
    eOesBusinessTypeT,

    # oes_base_model_credit.py
    OesCrdCreditAssetItemT,
    OesCrdDebtContractItemT, OesCrdDebtJournalItemT, OesCrdExcessStockItemT,
    OesCrdSecurityDebtStatsItemT, OesCrdUnderlyingInfoItemT,

    # oes_base_model_option_.py
    OesOptExerciseAssignItemT, OesOptUnderlyingHoldingItemT, OesOptionItemT,

    # oes_base_model.py
    OesOrdReqT, OesOrdCancelReqT, OesFundTrsfReqT,
    OesOrdItemT, OesTrdItemT, OesStkHoldingItemT,
    OesCashAssetItemT, OesEtfItemT, OesFundTransferSerialItemT,
    OesStockItemT, OesIssueItemT, OesLotWinningItemT,
    OesCommissionRateItemT, OesCrdCashRepayItemT,

    # oes_qry_packets.py
    OesCustItemT, OesInvAcctItemT, OesMarketStateItemT,
    OesEtfComponentItemT, OesCrdInterestRateItemT,
    OesQryCursorT, OesBrokerParamsInfoT,
    OesClientOverviewT, OesCounterCashItemT,
    OesQryOrdFilterT, OesQryTrdFilterT,
    OesQryStkHoldingFilterT, OesQryStockFilterT,
    OesQryCashAssetFilterT, OesQryCommissionRateFilterT,
    OesQryCustFilterT, OesQryEtfComponentFilterT, OesQryEtfFilterT,
    OesQryFundTransferSerialFilterT, OesQryInvAcctFilterT, OesQryIssueFilterT,
    OesQryLotWinningFilterT, OesQryMarketStateFilterT, OesQryNotifyInfoFilterT,

    # oes_qry_packets_credit.py
    OesCrdCashPositionItemT, OesCrdSecurityPositionItemT,
    OesCrdCollateralTransferOutMaxQtyItemT, OesCrdDrawableBalanceItemT,
    OesQryCrdCashPositionFilterT, OesQryCrdCashRepayFilterT,
    OesQryCrdCreditAssetFilterT, OesQryCrdDebtContractFilterT,
    OesQryCrdDebtJournalFilterT, OesQryCrdExcessStockFilterT,
    OesQryCrdInterestRateFilterT, OesQryCrdSecurityDebtStatsFilterT,
    OesQryCrdSecurityPositionFilterT, OesQryCrdUnderlyingInfoFilterT,

    # oes_qry_packets_option.py
    OesOptHoldingItemT, OesOptPositionLimitItemT, OesOptPurchaseLimitItemT,
    OesQryOptExerciseAssignFilterT, OesQryOptHoldingFilterT,
    OesQryOptPositionLimitFilterT, OesQryOptPurchaseLimitFilterT,
    OesQryOptUnderlyingHoldingFilterT, OesQryOptionFilterT,

    # oes_packets.py
    eOesMsgTypeT, OesRspMsgBodyT, OesApiSubscribeInfoT,
    OesNotifyInfoItemT, OesChangePasswordReqT, OesChangePasswordRspT,
    OesOptSettlementConfirmReqT,
)

from vendor.trade_api.c_api_wrapper import (
    OesAsyncApiContextParamsT, COesApiFuncLoader, OesMsgDispatcher,
    log_error, log_info
)

from vendor.trade_api.oes_spi import OesClientSpi


# ===================================================================
# 常量定义
# ===================================================================

# 默认的主配置区段名称
OESAPI_CFG_DEFAULT_SECTION                      = "oes_client"
# 默认的日志配置区段名称
OESAPI_CFG_DEFAULT_SECTION_LOGGER               = "log"
# 默认的委托申报配置项名称
OESAPI_CFG_DEFAULT_KEY_ORD_ADDR                 = "ordServer"
# 默认的执行报告配置项名称
OESAPI_CFG_DEFAULT_KEY_RPT_ADDR                 = "rptServer"
# 默认的查询服务配置项名称
OESAPI_CFG_DEFAULT_KEY_QRY_ADDR                 = "qryServer"

# 默认的异步API配置区段名称
OESAPI_CFG_DEFAULT_SECTION_ASYNC_API            = "async_api"
# 默认的CPU亲和性配置区段名称
OESAPI_CFG_DEFAULT_SECTION_CPUSET               = "cpuset"

MAX_BATCH_ORDER_LENGTH: int                     = 10000
# -------------------------


# ===================================================================
# 常量定义 (枚举类型定义)
# ===================================================================

class eOesApiChannelTypeT:
    """
    通道类型定义
    """
    OESAPI_CHANNEL_TYPE_ORDER                   = 1 # 委托申报通道
    OESAPI_CHANNEL_TYPE_REPORT                  = 2 # 回报通道
    OESAPI_CHANNEL_TYPE_QUERY                   = 3 # 查询通道
# -------------------------


class OesClientApi:
    """
    交易接口类
    """

    def __init__(self, config_file: str = '') -> None:
        """
        初始化 OesClientApi

        Args:
            config_file (str): [配置文件路径]
            - 取值为空 或 None, 需在MdsClientApi实例化后, 显示创建异步api运行时环境

        Raises:
            Exception: [description]
        """

        # TODO 版本检查
        self._oes_api_context: Optional[_Pointer] = None

        self._config_file: str = config_file
        if self._config_file and self._config_file.strip() != '':
            if self.create_context(config_file) is False:
                raise Exception("创建OES异步API的运行时环境失败! "
                    "config_file[{}]".format(config_file))

        self._oes_msg_dispatchers: List[OesMsgDispatcher] = []

        # 用于自动分配默认的 channel_tag
        self.current_channel_no: int = id(self)
        self.oes_spi: Optional[OesClientSpi] = None

        # 客户端委托流水号的序列 [key=clEnvid, value=clSeqNo]
        self._cl_seq_nos: Dict[int, int] = {}

        self._rpt_channels: Dict[str, tuple] = OrderedDict()
        self._ord_channels: Dict[str, tuple] = OrderedDict()
        self._default_ord_channel: Optional[_Pointer] = None
        self._default_rpt_channel: Optional[_Pointer] = None

        # 是否启动异步环境
        self._oes_api_started: bool = False
        self._oes_api_released: bool = False

    # ===================================================================
    # OES异步API接口函数封装 (上下文管理接口)
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def create_context(self, config_file: str) -> bool:
        """
        创建异步API的运行时环境 (通过配置文件和默认的配置区段加载相关配置参数)

        Args:
            config_file (str): [配置文件路径]
            - 取值为空 或 None, 需在OesClientApi实例化后, 显示创建异步api的运行时环境

        Returns:
            [bool]: [True: 创建成功; False: 创建失败]
        """
        if self._oes_api_context:
            raise Exception("重复创建异步API运行时环境, 执行失败! "
                "config_file[{}], oes_api_context[{}]".format(
                config_file, self._oes_api_context))

        self._oes_api_context = \
            COesApiFuncLoader().c_oes_async_api_create_context(config_file)

        return True if self._oes_api_context else False

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def create_context2(self, config_file: str, log_section: str,
            async_api_section: str, cpuset_section: str) -> bool:
        """
        创建异步API的运行时环境 (通过配置文件和指定的配置区段加载相关配置参数)

        Args:
            config_file (str): [配置文件路径]
            - 取值为空 或 None, 需在OesClientApi实例化后, 显示创建异步api的运行时环境
            log_section (str): [日志记录器的配置区段名称 (e.g. "log")]
            - 为空则忽略, 不初始化日志记录器
            async_api_section (str): [异步API扩展配置参数的配置区段名称 (e.g. "oes_client.async_api")]
            - 为空则忽略, 不加载异步API相关的扩展配置参数
            cpuset_section (str): [CPU亲和性配置的配置区段名称 (e.g. "cpuset")]
            - 为空则忽略, 不加载CPU亲和性配置

        Returns:
            [bool]: [True: 创建成功; False: 创建失败]
        """
        if self._oes_api_context:
            raise Exception("重复创建异步API运行时环境, 执行失败! "
                "config_file[{}], oes_api_context[{}]".format(
                config_file, self._oes_api_context))

        self._oes_api_context = \
            COesApiFuncLoader().c_oes_async_api_create_context2(
                config_file, log_section, async_api_section, cpuset_section)

        return True if self._oes_api_context else False

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def create_context_simple(self, log_conf_file: str,
            log_section: str, async_queue_size: int) -> bool:
        """
        创建异步API的运行时环境 (仅通过函数参数指定必要的配置参数)

        Args:
            log_conf_file (str): [日志配置文件路径]
            - 为空则忽略, 不初始化日志记录器
            log_section (str): [日志记录器的配置区段名称 (e.g. "log")]
            - 为空则使用默认值
            async_queue_size (int): [用于缓存行情数据的消息队列大小 (最大可缓存的消息数量)]
            - 为空则忽略, 不加载异步API相关的扩展配置参数

        Returns:
            [bool]: [True: 创建成功; False: 创建失败]
        """
        if self._oes_api_context:
            raise Exception("重复创建异步API运行时环境, 执行失败! "
                "config_file[{}], oes_api_context[{}]".format(
                log_conf_file, self._oes_api_context))

        self._oes_api_context = \
            COesApiFuncLoader().c_oes_async_api_create_context_simple(
                log_conf_file, log_section, async_queue_size)

        return True if self._oes_api_context else False

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def create_context_simple2(self,
            log_conf_file: str, log_section: str,
            context_params: OesAsyncApiContextParamsT) -> bool:
        """
        创建异步API的运行时环境 (仅通过函数参数指定必要的配置参数)

        Args:
            log_conf_file (str): [日志配置文件路径]
            - 为空则忽略, 不初始化日志记录器
            log_section (str): [日志记录器的配置区段名称 (e.g. "log")]
            - 为空则使用默认值
            context_params (OesAsyncApiContextParamsT): [上下文环境的创建参数]
            - 为空则使用默认值

        Returns:
            [bool]: [True: 创建成功; False: 创建失败]
        """
        if self._oes_api_context:
            raise Exception("重复创建异步API运行时环境, 执行失败! "
                "config_file[{}], oes_api_context[{}]".format(
                log_conf_file, self._oes_api_context))

        self._oes_api_context = \
            COesApiFuncLoader().c_oes_async_api_create_context_simple2(
                log_conf_file,
                log_section,
                byref(context_params) if context_params else None)

        return True if self._oes_api_context else False

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def register_spi(self,
            oes_client_spi: OesClientSpi,
            add_default_channel = False) -> bool:
        """
        注册默认的回调类，并根据需要自动创建默认的回调和委托通道

        Args:
            oes_client_spi (OesClientSpi): [回调类实例，用于处理默认通道的委托回报和查询结果]
            add_default_channel (bool, optional): [是否创建默认的回报通道和委托通道].
            - Defaults to False.

        Returns:
            [bool]: [True: 成功; False: 失败]
        """
        if self._oes_api_started:
            raise Exception('请在调用start前尝试!')

        if not isinstance(oes_client_spi, OesClientSpi):
            raise Exception(f"错误的oes_client_spi参数: {oes_client_spi} "
                            f"{type(oes_client_spi)}")

        if self.oes_spi:
            raise Exception("已经调用过register_handler")

        self.oes_spi = oes_client_spi
        oes_client_spi.oes_api = self

        if add_default_channel:
            if not self._config_file or self._config_file.strip() == '':
                raise Exception("执行register_spi函数并指定参数add_default_channel"
                        "为True时, 需同时指定OesClientApi._config_file配置文件名称")

            self.add_rpt_channel_from_file(oes_client_spi = oes_client_spi)
            self.add_ord_channel_from_file(oes_client_spi = oes_client_spi)

        return True

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def start(self) -> bool:
        """
        启动异步运行环境，调用前请确保已经无需再添加新的委托和回报通道, 启动后添加通道将不会生效

        Returns:
            [bool]: [True: 成功; False: 失败]
        """
        if self._oes_api_started:
            raise Exception("已经调用过start")

        if getattr(self, "_oes_api_released", False):
            raise Exception("已经调用过release")

        if not self._rpt_channels and not self._ord_channels:
            raise Exception("未找到有效通道，启动失败")

        if not COesApiFuncLoader().c_oes_async_api_start(self._oes_api_context):
            raise Exception("启动异步线程失败!")

        self._oes_api_started = True
        return True

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def release(self) -> bool:
        """
        清空资源，释放实例

        Returns:
            [bool]: [True: 成功; False: 失败]
        """
        if self._oes_api_started is False:
            raise Exception("尚未启动异步API, 无需释放资源")

        if getattr(self, "_oes_api_released", False):
            raise Exception("已经调用过release")

        self._oes_api_released = True
        self._oes_api_started = False

        COesApiFuncLoader().c_oes_async_api_stop(self._oes_api_context)
        time.sleep(0.05)

        while not self.is_all_terminated():
            log_info(">>> 正在等待回调线程等异步API线程安全退出...")
            time.sleep(1)

        COesApiFuncLoader().c_oes_async_api_release_context(
            self._oes_api_context)

        del self._oes_api_context
        del self._config_file
        del self._rpt_channels
        del self._ord_channels
        del self._default_ord_channel
        del self._default_rpt_channel
        del self.oes_spi

        for dpt in self._oes_msg_dispatchers:
            dpt.release()
        del self._oes_msg_dispatchers

        return True

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def is_api_running(self) -> bool:
        """
        返回异步API的通信线程是否正在运行过程中

        Returns:
            [bool]: [True: 运行中; False: 未运行或已终止运行]
        """
        return COesApiFuncLoader().c_oes_async_api_is_running(
            self._oes_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=True)
    def is_all_terminated(self) -> bool:
        """
        返回异步API相关的所有线程是否都已经安全退出 (或尚未运行)

        Returns:
            [bool]: [True: 安全退出; False: 未安全退出]
        """
        return COesApiFuncLoader().c_oes_async_api_is_all_terminated(
            self._oes_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=0)
    def get_total_picked(self) -> int:
        """
        返回异步API累计已提取和处理过的消息数量

        Returns:
            [int]: [异步API累计已提取和处理过的消息数量]
        """
        return COesApiFuncLoader().c_oes_async_api_get_total_picked(
            self._oes_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=0)
    def get_total_io_picked(self) -> int:
        """
        返回异步I/O线程累计已提取和处理过的消息数量

        Returns:
            [int]: [异步I/O线程累计已提取和处理过的消息数量]
        """
        return COesApiFuncLoader().c_oes_async_api_get_total_io_picked(
            self._oes_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=0)
    def get_async_queue_total_count(self) -> int:
        """
        返回异步API累计已入队的消息数量

        Returns:
            [int]: [异步API累计已入队的消息数量]
        """
        return COesApiFuncLoader().c_oes_async_api_get_async_queue_total_count(
            self._oes_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=0)
    def get_async_queue_remaining_count(self) -> int:
        """
        返回队列中尚未被处理的剩余数据数量

        Returns:
            [int]: [队列中尚未被处理的剩余数据数量]
        """
        return COesApiFuncLoader().c_oes_async_api_get_async_queue_remaining_count(
            self._oes_api_context)
    # -------------------------


    # ===================================================================
    # OES异步API接口函数封装 (通道管理接口)
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no=0)
    def get_channel_count(self) -> int:
        """
        返回通道数量 (通道配置信息数量)

        Returns:
            [int]: [通道数量 (通道配置信息数量)]
        """
        return COesApiFuncLoader().c_oes_async_api_get_channel_count(
            self._oes_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=0)
    def get_connected_channel_count(self) -> int:
        """
        返回当前已连接的通道数量

        Returns:
            [int]: [当前已连接的通道数量]
        """
        return COesApiFuncLoader().c_oes_async_api_get_connected_channel_count(
            self._oes_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def add_rpt_channel(self,
            channel_tag: str,
            remote_cfg: OesApiRemoteCfgT = None,
            user_info: Any = "",
            oes_client_spi: Optional[OesClientSpi] = None,
            copy_args: bool = True) -> OesAsyncApiChannelT:
        """
        添加回报通道配置信息

        Args:
            channel_tag (str): [通道标签]
            remote_cfg (OesApiRemoteCfgT): [待添加的通道配置信息 (不可为空)]
            user_info (Any): [用户回调参数]

            oes_client_spi (OesClientSpi]):
            [回报通道回报消息的处理函数类].
            - Defaults to None. 此时默认使用self.oes_spi

            copy_args (bool): [是否复制服务端返回的回报应答].
            - Defaults to True
            - 可手动设置成False, 会提升吞吐和降低时延，但是回报结果需要立即保存起来, 否则后期使用会因异步队列数据覆盖而无法访问的风险

        Returns:
            [OesAsyncApiChannelT]: [通道信息，请勿对其进行任何修改赋值操作]
        """
        return self.__add_channel_base_impl(False, False,
            channel_tag, user_info, oes_client_spi, copy_args,
            remote_cfg, "", "", "")

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def add_rpt_channel_from_file(self,
            channel_tag: str = "",
            config_file: str = "",
            config_section: str = OESAPI_CFG_DEFAULT_SECTION,
            addr_key: str = OESAPI_CFG_DEFAULT_KEY_RPT_ADDR,
            user_info: Any = "",
            oes_client_spi: OesClientSpi = None,
            copy_args: bool = True) -> OesAsyncApiChannelT:
        """
        从配置文件中加载并添加回报通道配置信息

        Args:
            channel_tag (str): [通道配置信息的自定义标签, 长度应小于32 (可以为空)]
            config_file (str): [配置文件路径 (不可为空)].
            config_section (str): [配置区段名称 (不可为空, e.g. "oes_client")]
            addr_key (str): [服务器地址的配置项关键字 (不可为空)]
            user_info (Any): [用户回调参数]

            oes_client_spi (OesClientSpi): [行情订阅通道消息的处理函数类].
            - Defaults to None. 此时默认使用self.oes_spi

            copy_args (bool): [是否复制服务端返回的回报应答].
            - Defaults to True
            - 可手动设置成False, 会提升吞吐和降低时延，但是行情数据需要立即保存起来, 否则后期使用会因异步队列数据覆盖而无法访问的风险

        Returns:
            [OesAsyncApiChannelT]: [通道信息，请勿对其进行任何修改赋值操作]
        """
        return self.__add_channel_base_impl(True, False,
            channel_tag, user_info, oes_client_spi, copy_args,
            None, config_file, config_section, addr_key)

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def add_ord_channel(self,
            channel_tag: str,
            remote_cfg: OesApiRemoteCfgT = None,
            user_info: Any = "",
            oes_client_spi: Optional[OesClientSpi] = None,
            copy_args: bool = True) -> OesAsyncApiChannelT:
        """
        添加委托通道配置信息
        Args:
            channel_tag (str): [通道标签]
            remote_cfg (OesApiRemoteCfgT): [待添加的通道配置信息 (不可为空)]
            user_info (Any): [用户回调参数]

            oes_client_spi (OesClientSpi]):
            [回报通道回报消息的处理函数类].
            - Defaults to None. 此时默认使用self.oes_spi

            copy_args (bool): [是否复制服务端返回的回报应答].
            - Defaults to True
            - 可手动设置成False, 会提升吞吐和降低时延，但是回报结果需要立即保存起来, 否则后期使用会因异步队列数据覆盖而无法访问的风险

        Returns:
            [OesAsyncApiChannelT]: [通道信息，请勿对其进行任何修改赋值操作]
        """
        return self.__add_channel_base_impl(False, True,
            channel_tag, user_info, oes_client_spi, copy_args,
            remote_cfg, "", "", "")

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def add_ord_channel_from_file(self,
            channel_tag: str = "",
            config_file: str = "",
            config_section: str = OESAPI_CFG_DEFAULT_SECTION,
            addr_key: str = OESAPI_CFG_DEFAULT_KEY_ORD_ADDR,
            user_info: Any = "",
            oes_client_spi: OesClientSpi = None,
            copy_args: bool = True) -> OesAsyncApiChannelT:
        """
        从配置文件中加载并添加委托通道配置信息

        Args:
            channel_tag (str): [通道配置信息的自定义标签, 长度应小于32 (可以为空)]
            config_file (str): [配置文件路径 (不可为空)].
            config_section (str): [配置区段名称 (不可为空, e.g. "oes_client")].
            addr_key (str): [服务器地址的配置项关键字 (不可为空)]
            user_info (Any): [用户回调参数]

            oes_client_spi (OesClientSpi): [行情订阅通道消息的处理函数类].
            - Defaults to None. 此时默认使用self.oes_spi

            copy_args (bool): [是否复制服务端返回的回报应答].
            - Defaults to True
            - 可手动设置成False, 会提升吞吐和降低时延，但是行情数据需要立即保存起来, 否则后期使用会因异步队列数据覆盖而无法访问的风险

        Returns:
            [OesAsyncApiChannelT]: [通道信息，请勿对其进行任何修改赋值操作]
        """
        return self.__add_channel_base_impl(True, True,
            channel_tag, user_info, oes_client_spi, copy_args,
            None, config_file, config_section, addr_key)

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def get_channel(self, channel_type: int = 0,
            channel_index: int = 0) -> OesAsyncApiChannelT:
        """
        返回顺序号对应的连接通道信息

        Args:
            channel_type (int): [通道类型]
            - 0: 任意类型
            - 1: 委托通道 (@see OESAPI_CHANNEL_TYPE_ORDER)
            - 2: 回报通道 (@see OESAPI_CHANNEL_TYPE_REPORT)
            channel_index (str): [通道顺序号]
            - 大于0: 返回与指定顺序号相对应的, 并且与指定通道类型相匹配的通道信息 (顺序号与通道配置的添加顺序一致)
            - 小于0: 返回第一个与指定通道类型相匹配的通道信息
            - INT_MAX: 返回最后一个与指定通道类型相匹配的通道信息

        Returns:
            [OesAsyncApiChannelT]: [通道信息，请勿对其进行任何修改赋值操作]
        """
        p_channel: _Pointer = \
            COesApiFuncLoader().c_oes_async_api_get_channel(
                self._oes_api_context, channel_type, channel_index)
        return p_channel.contents if p_channel else None

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def get_channel_by_tag(self, channel_type: int = 0,
            channel_tag: str = '') -> OesAsyncApiChannelT:
        """
        返回标签对应的连接通道信息

        Args:
            channel_type (int): [通道类型]
            - 0: 任意类型
            - 1: 委托通道 (@see OESAPI_CHANNEL_TYPE_ORDER)
            - 2: 回报通道 (@see OESAPI_CHANNEL_TYPE_REPORT)
            channel_tag (str): [通道配置信息的自定义标签]

        Returns:
            [OesAsyncApiChannelT]: [通道信息，请勿对其进行任何修改赋值操作]
        """
        p_channel: _Pointer = \
            COesApiFuncLoader().c_oes_async_api_get_channel_by_tag(
                self._oes_api_context, channel_type, channel_tag)
        return p_channel.contents if p_channel else None

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def is_channel_connected(self, channel: OesAsyncApiChannelT) -> bool:
        """
        返回通道是否已连接就绪

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]

        Returns:
            [bool]: [True: 已就绪; False: 未就绪]
        """
        return COesApiFuncLoader().c_oes_async_api_is_channel_connected(channel)

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def get_channel_cfg(self,
            channel: OesAsyncApiChannelT) -> OesAsyncApiChannelCfgT:
        """
        返回通道对应的配置信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]

        Returns:
            [OesAsyncApiChannelCfgT]: [通道配置信息]
        """
        channel_cfg: OesAsyncApiChannelCfgT = \
            COesApiFuncLoader().c_oes_async_api_get_channel_cfg(channel)
        return channel_cfg.contents if channel_cfg else None

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def get_channel_subscribe_cfg(self,
            channel: OesAsyncApiChannelT) -> OesApiSubscribeInfoT:
        """
        返回通道对应的行情订阅配置信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]

        Returns:
            [OesApiSubscribeInfoT]: [行情订阅配置信息]
        """
        subscribe_info: OesApiSubscribeInfoT = \
            COesApiFuncLoader().c_oes_async_api_get_channel_subscribe_cfg(
                channel)
        return subscribe_info.contents if subscribe_info else None
    # -------------------------


    # ===================================================================
    # 委托申报接口
    # ===================================================================
    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def send_order(self,
            channel: OesAsyncApiChannelT = None,
            req: OesOrdReqT = None) -> int:
        """
        发送委托申报请求
        - 以单向异步消息的方式发送委托申报到OES服务器
          OES的实时风控检查等处理结果将通过回报数据返回

        Args:
            channel (_Pointer]): [委托通道]
            - Defaults to None. 此时使用默认委托通道或者首个被添加的委托通道
            req (OesOrdReqT): [待发送的委托申报请求]

        Returns:
            int: [0: 成功; <0: 失败 (负的错误号)]
        """
        return COesApiFuncLoader().c_oes_async_api_send_order(
            channel or self.get_default_ord_channel(),
            req)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def send_cancel_order(self,
            channel: OesAsyncApiChannelT = None,
            req: OesOrdCancelReqT = None) -> int:
        """
        发送撤单请求

        - 以单向异步消息的方式发送委托申报到OES服务器
          OES的实时风控检查等处理结果将通过回报数据返回

        Args:
            channel (Optional[_Pointer], optional): [委托通道]
            - Defaults to None. 此时使用默认委托通道或者首个被添加的委托通道

            req (OesOrdCancelReqT): [待发送的撤单请求]
            - 需要填充以下字段
              - mktId, 原始订单(待撤销的订单)的市场代码
              - origClSeqNo, 原始订单(待撤销的订单)的客户委托流水号
                (若使用 origClOrdId, 则不必填充该字段)
              - origClEnvId, 原始订单(待撤销的订单)的客户端环境号
                (小于等于0, 则使用当前会话的 clEnvId)
              - origClOrdId，原始订单(待撤销的订单)的订单号

        Returns:
            int: [0: 成功; <0: 失败 (负的错误号)]
        """
        return COesApiFuncLoader().c_oes_async_api_send_cancel_order(
            channel or self.get_default_ord_channel(),
            byref(req) if req else None)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def send_batch_orders(self,
            channel: OesAsyncApiChannelT = None,
            reqs: List[OesOrdReqT] = None) -> int:
        """
        批量发送多条委托请求
        - 以批量的形式同时发送多笔委托申报
          而风控检查等处理结果则仍以单笔委托为单位通过回报数据返回
        - 批量委托的委托请求填充规则与单条委托完全相同, 回报处理规则也与单条委托完全相同
          - 当初始化时auto_set_seq_no为True且req.clSeqNo为未被有效设置的情况下
            客户端将自动使用对应通道最新有效流水号进行填充
          - 每笔委托请求的 "客户委托流水号(clSeqNo)" 如填充需要维持在同一客户端下的唯一性
          - 服务器端的处理结果则仍将以单笔委托为单位通过回报数据返回
        - 批量委托接口支持的委托数量限制
          - 批量委托接口最大允许传入的委托数量上限为: 10000 笔委托
          - 批量委托接口可一次性原子发送的最大委托数量为: 500 笔委托
            超过该数量将自动拆分为多次提交

        Args:
            channel (Optional[_Pointer], optional): [委托通道]
            - Defaults to None. 此时使用默认委托通道或者首个被添加的委托通道
            reqs (List[OesOrdReqT]): [待发送的委托请求列表，单次数量上限为10000]

        Returns:
            int: [0: 成功; <0: 失败 (负的错误号)]
        """
        if len(reqs) > MAX_BATCH_ORDER_LENGTH:
            raise Exception(f"{len(reqs)}超过单次允许发送请求数量:{MAX_BATCH_ORDER_LENGTH}")

        return COesApiFuncLoader().c_oes_async_api_send_batch_orders(
                channel or self.get_default_ord_channel(),
                (POINTER(OesOrdReqT) * len(reqs)) (*[pointer(req) for req in reqs]),
                len(reqs))

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def send_fund_trsf(self,
            channel: OesAsyncApiChannelT = None,
            req: OesFundTrsfReqT = None) -> int:
        """
        发送出入金委托请求

        - 以单向异步消息的方式发送委托申报到OES服务器
          OES的实时风控检查等处理结果将通过回报数据返回

        - 关于 "出入金的发生金额 (occurAmt)"
          - 无论入金还是出金, 发生金额的取值都应为正数
          - 精度将被自动向下舍入到分, 例如: 金额 1.9999 将被自动转换为 1.9900

        Args:
            channel (Optional[_Pointer], optional): [委托通道]
            - Defaults to None. 此时使用默认委托通道或者首个被添加的委托通道
            req (OesFundTrsfReqT): [待发送的出入金委托请求]

        Returns:
            int: [0: 成功; <0: 失败 (负的错误号)]
        """
        return COesApiFuncLoader().c_oes_async_api_send_fund_transfer(
            channel or self.get_default_ord_channel(),
            req)
    # -------------------------


    # ===================================================================
    # 融资融券业务特有的委托接口
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def send_credit_repay_req(self,
            channel: OesAsyncApiChannelT = None,
            req: OesOrdReqT = None,
            repay_mode: int = 0,
            debt_id: str = "") -> int:
        """
        发送可以指定待归还合约编号的融资融券负债归还请求
        - 与 send_order 接口的异同
          - 行为与 send_order 接口完全一致, 只是可以额外指定待归还的合约编号和归还模式
          - 如果不需要指定待归还的合约编号和归还模式，也直接可以使用 send_order 接口完成相同的工作
          - 以单向异步消息的方式发送委托申报到OES服务器, OES的实时风控检查等处理结果将通过回报数据返回
          - 回报数据也与普通委托的回报数据完全相同
          - 当初始化时auto_set_seq_no为True且req.clSeqNo为未被有效设置的情况下, 客户端将自动使用对应通道最新有效流水号进行填充

        - 支持的业务范围:
          - 卖券还款
          - 买券还券
          - 直接还券

        @note 本接口不支持直接还款, 直接还款需要使用 send_credit_cash_repay_req 接口

        Args:
            channel (Optional[_Pointer], optional): [委托通道]
            - Defaults to None. 此时使用默认委托通道或者首个被添加的委托通道

            req (OesOrdReqT): [待发送的委托申报请求]

            repay_mode (int): [归还模式 (0:默认, 10:仅归还息费)]. Defaults to 0
            - 归还模式为默认时, 不会归还融券合约的息费
            - 如需归还融券合约的息费, 需指定为'仅归还息费'模式
              (最终能否归还取决于券商是否支持该归还模式)

            debt_id (str, optional): [归还的合约编号 (可以为空)]. Defaults to "".
            - 若为空, 则依次归还所有融资融券合约
            - 若不为空, 则优先归还指定的合约编号, 剩余的资金或股份再依次归还其它融资融券合约

        Returns:
            int: [0: 成功; <0: 失败 (负的错误号)]
        """
        return COesApiFuncLoader().c_oes_async_api_send_credit_repay_req(
            channel or self.get_default_ord_channel(),
            req,
            repay_mode,
            debt_id or CHAR_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def send_credit_cash_repay_req(self,
            channel: OesAsyncApiChannelT = None,
            cl_seq_no: int = -1,
            repay_amt: int = 0,
            repay_mode: int = 0,
            debt_id: str = "",
            user_info: Optional[UnionForUserInfo] = None) -> int:
        """
        发送直接还款(现金还款)请求

        Args:
            channel (Optional[_Pointer], optional): [委托通道]
            - Defaults to None. 此时使用默认委托通道或者首个被添加的委托通道

            cl_seq_no (int, optional): [客户委托流水号]. Defaults to -1.
            - <=0时，客户端将自动使用对应通道最新有效流水号进行填充

            repay_amt (int): [归还金额 (单位精确到元后四位, 即1元 = 10000)]
            - @note 实际还款金额会向下取整到分

            repay_mode (int): [归还模式 (0:默认, 10:仅归还息费)]. Defaults to 0
            - 归还模式为默认时, 不会归还融券合约的息费
            - 如需归还融券合约的息费, 需指定为'仅归还息费'模式
              (最终能否归还取决于券商是否支持该归还模式)

            debt_id (str, optional): [归还的合约编号 (可以为空)]. Defaults to "".
            - 若为空, 则依次归还所有融资融券合约
            - 若不为空, 则优先归还指定的合约编号, 剩余的资金或股份再依次归还其它融资融券合约

            user_info (Optional[UnionForUserInfo], optional):
            [用户私有信息 (可以为空, 由客户端自定义填充, 并在回报数据中原样返回)].
            Defaults to None.
            - 同委托请求信息中的 userInfo 字段
            - 数据类型为: char[8] 或 uint64, int32[2] 等

        Returns:
            int: [0成功， <0失败(负的错误号)]
        """
        return COesApiFuncLoader().c_oes_async_api_send_credit_cash_repay_req(
            channel or self.get_default_ord_channel(),
            cl_seq_no,
            repay_amt,
            repay_mode,
            debt_id or CHAR_NULLPTR,
            byref(user_info) if user_info else VOID_NULLPTR)
    # -------------------------


    # ===================================================================
    # 期权业务特有的委托接口
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def send_opt_settlement_confirm(self,
            channel: OesAsyncApiChannelT = None,
            req: OesOptSettlementConfirmReqT = None) -> int:
        """
        期权账户结算单确认
        - 以单向异步消息的方式发送委托申报到OES服务器
          OES的实时风控检查等处理结果将通过回报数据返回
        - 结算单确认后, 方可进行委托申报和出入金请求

        Args:
            channel (Optional[_Pointer], optional): [委托通道]
            - Defaults to None. 此时使用默认委托通道或者首个被添加的委托通道
            req (OesOptSettlementConfirmReqT): [待发送的结算单确认请求]

        Returns:
            int: [0: 成功; <0: 失败 (负的错误号)]
        """
        return COesApiFuncLoader().c_oes_async_api_send_opt_settlement_confirm_req(
            channel or self.get_default_ord_channel(),
            req)
    # -------------------------


    # ===================================================================
    # OES异步API接口函数封装 (密码修改接口函数声明)
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def send_change_password_req(self,
            channel: OesAsyncApiChannelT = None,
            req: OesChangePasswordReqT = None) -> int:
        """
        发送密码修改请求(修改客户端登录密码)
        密码修改请求通过查询通道发送到OES服务器, 并采用请求 / 应答的方式直接返回处理结果

        Args:
            channel (OesAsyncApiChannelT): [查询通道]
            req (OesChangePasswordReqT): [待发送的密码修改请求]

        Returns:
            [int]: [=0: 成功; >0: API调用失败 (负的错误号); <0: 服务端业务处理失败 (OES错误号)]
        """
        change_password_rsp = OesChangePasswordRspT()

        return COesApiFuncLoader().c_oes_async_api_send_change_password_req(
            channel or self.get_default_ord_channel(),
            byref(req) if req else None,
            byref(change_password_rsp))
    # -------------------------


    # ===================================================================
    # OES异步API接口函数封装 (会话管理接口)
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def send_report_synchronization(self,
            channel: OesAsyncApiChannelT,
            subscribe_env_id: int = 0,
            subscribe_rpt_types: int = 0,
            last_rpt_seq_num: int = 0) -> bool:
        """
        发送回报同步消息 (仅适用于回报通道)

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            subscribe_env_id (int): [待订阅的客户端环境号]
            - 大于0, 区分环境号, 仅订阅环境号对应的回报数据
            - 等于0, 不区分环境号, 订阅该客户下的所有回报数据
            - 小于0, 复用添加通道时指定的默认配置
              - @note 此处与同步API不同. 小于0时, 同步API为不区分环境号
            subscribe_rpt_types (int): [待订阅的回报消息种类]
            - e.g. OES_SUB_RPT_TYPE_ORDER_INSERT
                    | OES_SUB_RPT_TYPE_ORDER_REPORT
                    | OES_SUB_RPT_TYPE_TRADE_REPORT)
            - @see eOesSubscribeReportTypeT
              - 小于0, 复用添加通道时指定的默认配置
                - @note 此处与同步API不同. 小于0时, 同步API为订阅所有类型的消息
            last_rpt_seq_num (int): [客户端最后接收到的回报数据的回报编号]
            - 等于0, 从头开始推送回报数据
            - 大于0, 从指定的回报编号开始推送回报数据
            - 小于0, 从上次接收到的断点位置开始
              - @note 此处与同步API不同. 小于0时, 同步API为从最新的数据开始推送回报数据
              - 如果明确需要只从最新的数据开始推送回报数据, 可以指定一个特别大的数 (例如 INT_MAX)

        Returns:
            [int]: [=0: 成功
                    >0: 处理失败, 将重建连接并继续尝试执行
                    <0: 处理失败, 异步API将中止运行
                   ]
        """
        return COesApiFuncLoader().c_oes_async_api_send_report_synchronization(
            channel, subscribe_env_id, subscribe_rpt_types, last_rpt_seq_num)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def send_heart_beat(self, channel: OesAsyncApiChannelT) -> bool:
        """
        发送心跳消息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]

        Returns:
            [bool]: [TRUE 成功; FALSE 失败]
        """
        return COesApiFuncLoader().c_oes_async_api_send_heart_beat(channel)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def send_test_req(self, channel: OesAsyncApiChannelT,
            test_req_id: str, test_req_id_size: int) -> bool:
        """
        发送测试消息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            test_req_id (str): [测试请求标识符 (C32, 可以为空)]
            test_req_id_size (int): [测试请求标识符的长度]

        Returns:
            [bool]: [TRUE 成功; FALSE 失败]
        """
        return COesApiFuncLoader().c_oes_async_api_send_test_req(
            channel, test_req_id, test_req_id_size)
    
    @spk_decorator_exception(log_error=log_error, error_no=1)
    def default_on_connect(self, channel: OesAsyncApiChannelT) -> int:
        """
        连接完成后处理的默认实现

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]

        Returns:
            [int]: [=0: 成功
                  >0: 处理失败, 将重建连接并继续尝试执行
                  <0: 处理失败, 异步API将中止运行
                  ]
        """
        return COesApiFuncLoader().c_oes_async_api_default_on_connect(
            channel, VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=1)
    def subscribe_nothing_on_connect(self, channel: OesAsyncApiChannelT) -> int:
        """
        连接完成后处理的默认实现 (不订阅任何行情数据)

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]

        Returns:
            [int]: [=0: 成功
                  >0: 处理失败, 将重建连接并继续尝试执行
                  <0: 处理失败, 异步API将中止运行
                  ]
        """
        return COesApiFuncLoader().c_oes_async_api_subscribe_nothing_on_connect(
            channel, VOID_NULLPTR)
    # -------------------------


    # ===================================================================
    # OES异步API接口函数封装 (辅助的配置管理接口)
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_preconnect_able(self, is_preconnect_able: bool) -> bool:
        """
        设置是否在启动前预创建并校验所有的连接

        Args:
            is_preconnect_able (bool): [是否在启动前预创建并校验所有的连接]
            - TRUE: 启动前预创建并校验所有的连接, 如果连接失败则中止启动
            - FALSE: 启动前不预先创建和校验连接 (默认行为)

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        return COesApiFuncLoader().c_oes_async_api_set_preconnect_able(
            self._oes_api_context, is_preconnect_able)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def is_preconnect_able(self) -> bool:
        """
        返回是否在启动前预创建并校验所有的连接

        Returns:
            [bool]: [True: 是; False: 否]
        """
        return COesApiFuncLoader().c_oes_async_api_is_preconnect_able(
            self._oes_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_async_callback_able(self, is_async_callback_able: bool) -> bool:
        """
        设置是否启动独立的回调线程来执行回调处理

        Args:
            is_async_callback_able (bool): [是否启动独立的回调线程来执行回调处理]
            - TRUE: 创建单独的回调线程
            - FALSE: 不启动单独的回调线程, 直接在通信线程下执行回调处理 (默认行为)

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        return COesApiFuncLoader().c_oes_async_api_set_async_callback_able(
            self._oes_api_context, is_async_callback_able)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def is_async_callback_able(self) -> bool:
        """
        返回是否启动独立的回调线程来执行回调处理

        Returns:
            [bool]: [True: 是; False: 否]
        """
        return COesApiFuncLoader().c_oes_async_api_is_async_callback_able(
            self._oes_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def get_async_queue_length(self) -> int:
        """
        返回异步通信队列的长度 (可缓存的最大消息数量)

        Returns:
            [int]: [异步通信队列的长度 (可缓存的最大消息数量)]
        """
        return COesApiFuncLoader().c_oes_async_api_get_async_queue_length(
            self._oes_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def get_async_queue_data_area_size(self) -> int:
        """
        返回异步通信队列的数据空间大小

        Returns:
            [int]: [异步通信队列的数据空间大小]
        """
        return COesApiFuncLoader().\
            c_oes_async_api_get_async_queue_data_area_size(
                self._oes_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_builtin_query_able(self, is_builtin_query_able: bool) -> bool:
        """
        设置是否启用内置的查询通道

        Args:
            is_builtin_query_able (bool): [是否启用内置的查询通道]
            - 如果将该参数设置为TRUE, 则启动异步API时将自动创建一个与行情查询服务的连接
            - 如果不需要通过异步API查询行情数据的话, 可以将该参数设置为FALSE, 这样可以避免额外占用一个查询通道的连接数量
            - 不指定的话, 默认为FALSE

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        return COesApiFuncLoader().c_oes_async_api_set_builtin_query_able(
            self._oes_api_context, is_builtin_query_able)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def is_builtin_query_able(self) -> bool:
        """
        返回是否启用内置的查询通道

        Returns:
            [bool]: [True: 是; False: 否]
        """
        return COesApiFuncLoader().c_oes_async_api_is_builtin_query_able(
            self._oes_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def is_builtin_query_channel_connected(self,
            channel: OesAsyncApiChannelT = None) -> bool:
        """
        返回内置的查询通道是否已连接就绪

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

        Returns:
            [bool]: [True: 是; False: 否]
        """
        return COesApiFuncLoader().\
            c_oes_async_api_is_builtin_query_channel_connected(channel)
    # -------------------------
    
    
    # ===================================================================
    # OES异步API接口函数封装 (查询接口)
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no='')
    def get_api_version(self) -> str:
        """
        获取API的发行版本号

        Returns:
            [str]: [API的发行版本号 (如: "0.15.3")]
        """
        return COesApiFuncLoader().c_oes_async_api_get_api_version().decode()

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def get_trading_day(self,
            channel: OesAsyncApiChannelT = None) -> int:
        """
        获取当前交易日

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

        Returns:
            [int]: [>=0: 当前交易日(格式: YYYYMMDD); <0: 负的错误号]
        """
        return COesApiFuncLoader().c_oes_async_api_get_trading_day(
            channel or self.get_default_channel())

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def get_client_overview(self,
            channel: OesAsyncApiChannelT = None) -> OesClientOverviewT:
        """
        获取客户端总览信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

        Returns:
            [OesClientOverviewT]: [查询到的客户端总览信息]
        """
        overview: OesClientOverviewT = OesClientOverviewT()

        ret: int = COesApiFuncLoader().c_oes_async_api_get_client_overview(
            channel or self.get_default_channel(),
            overview)

        return overview if ret == 0 else None

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_cust_info(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryCustFilterT = None,
            user_info: Any = None) -> int:
        """
        查询客户信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryCustFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_cust_info(
            _channel,
            qry_filter or None,
            self.__get_oes_msg_dispatcher_by_channel(
                _channel).handle_qry_msg(user_info),
            VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_inv_acct(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryInvAcctFilterT = None,
            user_info: Any = None) -> int:
        """
        查询证券账户信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryInvAcctFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_inv_acct(
            _channel,
            qry_filter or None,
            self.__get_oes_msg_dispatcher_by_channel(
                _channel).handle_qry_msg(user_info),
            VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_stock(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryStockFilterT = None,
            user_info: Any = None) -> int:
        """
        查询现货产品信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryStockFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_stock(
            _channel,
            qry_filter or None,
            self.__get_oes_msg_dispatcher_by_channel(
                _channel).handle_qry_msg(user_info),
            VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_issue(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryIssueFilterT = None,
            user_info: Any = None) -> int:
        """
        查询证券发行产品信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryIssueFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_issue(
            _channel,
            qry_filter or None,
            self.__get_oes_msg_dispatcher_by_channel(
                _channel).handle_qry_msg(user_info),
            VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_etf(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryEtfFilterT = None,
            user_info: Any = None) -> int:
        """
        查询ETF申赎产品信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryEtfFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_etf(
            _channel,
            qry_filter or None,
            self.__get_oes_msg_dispatcher_by_channel(
                _channel).handle_qry_msg(user_info),
            VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_etf_component(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: Optional[OesQryEtfComponentFilterT] = None,
            user_info: Any = None) -> int:
        """
        查询ETF成份证券信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryEtfComponentFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_etf_component(
            _channel,
            qry_filter or None,
            self.__get_oes_msg_dispatcher_by_channel(
                _channel).handle_qry_msg(user_info),
            VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_cash_asset(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: Optional[OesQryCashAssetFilterT] = None,
            user_info: Any = None) -> int:
        """
        查询客户资金信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryCashAssetFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_cash_asset(
            _channel,
            qry_filter or None,
            self.__get_oes_msg_dispatcher_by_channel(
                _channel).handle_qry_msg(user_info),
            VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def get_colocation_peer_cash_asset(self,
            channel: OesAsyncApiChannelT = None,
            cash_acct_id: str = "") -> OesCashAssetItemT:
        """
        查询两地交易时对端结点的资金资产信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            cash_acct_id (str): [资金账号 (可以为空)]
            - Defaults to "", 此时返回当前连接对应的第一个客户的资金账户的对端结点资金资产信息

        Returns:
            OesCashAssetItemT: [查询到的对端结点资金资产信息]
        """
        cash_asset_item: OesCashAssetItemT = OesCashAssetItemT()

        ret: int = COesApiFuncLoader().c_oes_async_api_get_colocation_peer_cash_asset(
            channel or self.get_default_channel(),
            cash_acct_id or CHAR_NULLPTR,
            cash_asset_item)

        return cash_asset_item if ret == 0 else None

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def get_counter_cash(self,
            channel: OesAsyncApiChannelT = None,
            cash_acct_id: str = "") -> OesCounterCashItemT:
        """
        查询主柜资金信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            cash_acct_id (str): [资金账号 (可以为空)]
            - Defaults to "". 此时返回当前连接对应的第一个客户的资金账户的资金资产信息

        Returns:
            OesCounterCashItemT: [查询到的主柜资金信息]
        """
        counter_cash_item: OesCounterCashItemT = OesCounterCashItemT()

        ret: int = COesApiFuncLoader().c_oes_async_api_get_counter_cash(
            channel or self.get_default_channel(),
            cash_acct_id or CHAR_NULLPTR,
            counter_cash_item)

        return counter_cash_item if ret == 0 else None

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_stk_holding(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryStkHoldingFilterT = None,
            user_info: Any = None) -> int:
        """
        查询股票持仓信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryStkHoldingFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_stk_holding(
            _channel,
            qry_filter or None,
            self.__get_oes_msg_dispatcher_by_channel(
                _channel).handle_qry_msg(user_info),
            VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_lot_winning(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryLotWinningFilterT = None,
            user_info: Any = None) -> int:
        """
        查询新股配号、中签信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryLotWinningFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_lot_winning(
            _channel,
            qry_filter or None,
            self.__get_oes_msg_dispatcher_by_channel(
                _channel).handle_qry_msg(user_info),
            VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_order(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryOrdFilterT = None,
            user_info: Any = None) -> int:
        """
        查询所有委托信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryOrdFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_order(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_trade(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryTrdFilterT = None,
            user_info: Any = None) -> int:
        """
        查询成交信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryTrdFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_trade(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_fund_transfer_serial(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryFundTransferSerialFilterT = None,
            user_info: Any = None) -> int:
        """
        查询出入金流水

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryFundTransferSerialFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_fund_transfer_serial(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_commission_rate(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: Optional[OesQryCommissionRateFilterT] = None,
            user_info: Any = None) -> int:
        """
        查询佣金信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryCommissionRateFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_commission_rate(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_market_state(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: Optional[OesQryMarketStateFilterT] = None,
            user_info: Any = None) -> int:
        """
        查询市场状态信息
        @目前仅深圳交易所各个交易平台的市场状态信息有效

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryMarketStateFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_market_state(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_notify_info(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryNotifyInfoFilterT = None,
            user_info: Any = None) -> int:
        """
        查询通知消息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryNotifyInfoFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_notify_info(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def query_broker_params_info(self,
            channel: OesAsyncApiChannelT = None) -> OesBrokerParamsInfoT:
        """
        获取券商参数信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

        Return:
            OesBrokerParamsInfoT: [查询到的券商参数信息]
        """
        broker_params_info: OesBrokerParamsInfoT = OesBrokerParamsInfoT()

        ret: int = COesApiFuncLoader().c_oes_async_api_query_broker_params_info(
            channel or self.get_default_channel(),
            broker_params_info)

        return broker_params_info if ret == 0 else None


    # ===================================================================
    # OES异步API接口函数封装 (期权业务特有的查询接口)
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_option(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryOptionFilterT = None,
            user_info: Any = None) -> int:
        """
        查询期权产品信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryOptionFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_option(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_opt_holding(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryOptHoldingFilterT = None,
            user_info: Any = None) -> int:
        """
        查询期权持仓信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryOptHoldingFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_opt_holding(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_opt_underlying_holding(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryOptUnderlyingHoldingFilterT = None,
            user_info: Any = None) -> int:
        """
        查询期权标的持仓信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryOptUnderlyingHoldingFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_opt_underlying_holding(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_opt_position_limit(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: Optional[OesQryOptPositionLimitFilterT] = None,
            user_info: Any = None) -> int:
        """
        查询期权限仓额度信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryOptPositionLimitFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_opt_position_limit(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_opt_purchase_limit(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryOptPurchaseLimitFilterT = None,
            user_info: Any = None) -> int:
        """
        查询期权限购额度信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryOptPurchaseLimitFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_opt_purchase_limit(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_opt_exercise_assign(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryOptExerciseAssignFilterT = None,
            user_info: Any = None) -> int:
        """
        查询期权行权指派信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryOptExerciseAssignFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_opt_exercise_assign(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def get_opt_settlement_statement(self,
            channel: OesAsyncApiChannelT = None,
            cust_id: str = "") -> str:
        """
        查询期权结算单信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            cust_id (str): [客户代码 (可以为空)]. Defaults to ""

        Returns:
            str: [结算单信息]
        """
        OPT_SETTLEMENT_STATEMENT_BUF_SIZE: int = 512 * 1024  # 512k

        buf: Array[c_char] = create_string_buffer(
            OPT_SETTLEMENT_STATEMENT_BUF_SIZE)

        ret: int = COesApiFuncLoader().c_oes_async_api_query_opt_settlement_statement(
            channel or self.get_default_channel(),
            cust_id or CHAR_NULLPTR,
            buf,
            OPT_SETTLEMENT_STATEMENT_BUF_SIZE)

        return buf.value.decode() if ret >= 0 else None
    # -------------------------


    # ===================================================================
    # OES异步API接口函数封装 (融资融券业务特有的查询接口)
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_crd_credit_asset(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryCrdCreditAssetFilterT = None,
            user_info: Any = None) -> int:
        """
        查询信用资产信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryCrdCreditAssetFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_crd_credit_asset(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_crd_underlying_info(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryCrdUnderlyingInfoFilterT = None,
            user_info: Any = None) -> int:
        """
        查询客户的融资融券可充抵保证金证券及融资融券标的信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryCrdUnderlyingInfoFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_crd_underlying_info(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_crd_cash_position(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryCrdCashPositionFilterT = None,
            user_info: Any = None) -> int:
        """
        查询融资融券资金头寸信息(可融资头寸信息)

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryCrdCashPositionFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_crd_cash_position(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_crd_security_position(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryCrdSecurityPositionFilterT = None,
            user_info: Any = None) -> int:
        """
        查询融资融券证券头寸信息(可融券头寸信息)

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryCrdSecurityPositionFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_crd_security_position(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_crd_holding(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryStkHoldingFilterT = None,
            user_info: Any = None) -> int:
        """
        查询信用持仓信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryStkHoldingFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_crd_holding(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_crd_debt_contract(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: Optional[OesQryCrdDebtContractFilterT] = None,
            user_info: Any = None) -> int:
        """
        查询融资融券合约信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryCrdDebtContractFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_crd_debt_contract(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_crd_debt_journal(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryCrdDebtJournalFilterT = None,
            user_info: Any = None) -> int:
        """
        查询融资融券合约流水信息
        @note 仅查询当日流水

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryCrdDebtJournalFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_crd_debt_journal(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_crd_cash_repay_order(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryCrdCashRepayFilterT = None,
            user_info: Any = None) -> int:
        """
        查询融资融券直接还款委托信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryCrdCashRepayFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_crd_cash_repay_order(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_crd_security_debt_stats(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryCrdSecurityDebtStatsFilterT = None,
            user_info: Any = None) -> int:
        """
        查询融资融券客户单证券负债统计信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryCrdSecurityDebtStatsFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_crd_security_debt_stats(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_crd_excess_stock(self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryCrdExcessStockFilterT = None,
            user_info: Any = None) -> int:
        """
        查询融资融券余券信息

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryCrdExcessStockFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_crd_excess_stock(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_crd_interest_rate( self,
            channel: OesAsyncApiChannelT = None,
            qry_filter: OesQryCrdInterestRateFilterT = None,
            user_info: Any = None) -> int:
        """
        查询融资融券息费利率

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

            qry_filter (OesQryCrdInterestRateFilterT): [过滤条件]
            user_info (Any): [用户回调参数]

        Returns:
            int: [>=0: 查询到的记录数; <0: 失败(负的错误号)]
        """
        _channel: OesAsyncApiChannelT = \
            channel or self.get_default_channel()

        return COesApiFuncLoader().c_oes_async_api_query_crd_interest_rate(
                _channel,
                qry_filter or None,
                self.__get_oes_msg_dispatcher_by_channel(
                    _channel).handle_qry_msg(user_info),
                VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def get_crd_drawable_balance(self,
            channel: OesAsyncApiChannelT = None) -> OesCrdDrawableBalanceItemT:
        """
        查询融资融券业务最大可取资金

        Args:
            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

        Returns:
            OesCrdDrawableBalanceItemT: [查询到的可取资金信息]
        """
        balance: OesCrdDrawableBalanceItemT = OesCrdDrawableBalanceItemT()

        ret: int = COesApiFuncLoader().c_oes_async_api_get_crd_drawable_balance(
            channel or self.get_default_channel(),
            byref(balance))

        return balance if ret >= 0 else None

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def get_crd_collateral_transfer_out_max_qty(self,
            channel: OesAsyncApiChannelT = None,
            security_id: str = '',
            mkt_id: int = 0) -> OesCrdCollateralTransferOutMaxQtyItemT:
        """
        查询融资融券担保品可转出的最大数量

        Args:
            security_id (str): [证券代码 (不可为空)]
            mkt_id (int): [市场代码] @see eOesMarketIdT

            channel (OesAsyncApiChannelT): [异步API的连接通道信息]
            - 委托通道或回报通道均可
            - Defaults to None. 默认使用首个被添加的委托或回报通道

        Returns:
            OesCrdCollateralTransferOutMaxQtyItemT: [查询到的担保品可转出最大数量信息]
        """
        transfer_out_max_qty_item: OesCrdCollateralTransferOutMaxQtyItemT = \
            OesCrdCollateralTransferOutMaxQtyItemT()

        ret: int = COesApiFuncLoader().c_oes_async_api_get_crd_collateral_transfer_out_max_qty(
            channel or self.get_default_channel(),
            security_id,
            mkt_id,
            transfer_out_max_qty_item)

        return transfer_out_max_qty_item if ret >= 0 else None
    # -------------------------


    # ===================================================================
    # OES异步API接口函数封装 (辅助函数)
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def init_logger(self, config_file: str, logger_section: str) -> bool:
        """
        初始化日志记录器

        Args:
            config_file (str): [配置文件路径]
            logger_section (str): [配置区段名称]

        Returns:
            [bool]: [TRUE 成功; FALSE 失败]
        """
        return COesApiFuncLoader().c_oes_api_init_logger(
            config_file or CHAR_NULLPTR,
            logger_section or CHAR_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def init_logger_direct(self, log_mode: str, min_log_level: str,
            log_file_path: str, max_file_length: int,
            max_backup_count: int) -> bool:
        """
        直接通过指定的参数初始化日志记录器

        Args:
            log_mode (str): [日志模式]
            - 取值说明:
              - FILE              : 文件日志 - 等同于 FILE_ROLLING (轮换, 不区分具体日期)
              - FILE_ROLLING      : 文件日志 - 轮换, 不区分具体日期
              - FILE_DAILY        : 文件日志 - 每天一个日志文件
              - FILE_DAILY_ROLLING: 文件日志 - 每天N个日志文件 (N >= 1)
              - CONSOLE           : 控制台日志 - 等同于 CONSOLE_STDOUT (输出到标准输出)
              - CONSOLE_STDOUT    : 控制台日志 - 输出到标准输出 (stdout)
              - CONSOLE_STDERR    : 控制台日志 - 输出到标准错误 (stderr)
            min_log_level (str): [日志登记的起始级别]
            - 日志级别列表 (级别从低到高):
              - 跟踪信息 (TRACE)
              - 调试信息 (DEBUG)
              - 提示信息 (INFO)
              - 警告信息 (WARN)
              - 错误信息 (ERROR)
              - 业务提示 (BZINF, BZ_INFO)
              - 业务警告 (BZWRN, BZ_WARN)
              - 业务错误 (BZERR, BZ_ERROR)
              - 致命错误 (FATAL)
              - 屏蔽所有日志 (NONE)
            log_file_path (str): [日志文件路径]
            max_file_length (int): [日志文件最大长度]
            - 取值小于0, 表示无最大长度限制
            - 取值等于0, 将使用默认值 (400M)
            max_backup_count (int): [日志文件最大备份数]
            - 轮换(ROLLING)模式下的最大保留的历史日志文件数量
            - 取值小于0, 表示不保留备份文件
            - 取值等于0, 将使用默认值 (3)

        Returns:
            [bool]: [TRUE 成功; FALSE 失败]
        """
        return COesApiFuncLoader().c_oes_api_init_logger_direct(
            log_mode or CHAR_NULLPTR,
            min_log_level or CHAR_NULLPTR,
            log_file_path or CHAR_NULLPTR,
            max_file_length, max_backup_count)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def parse_config_from_file(self, config_file_name: str,
            section: str, addr_key: str, remote_cfg: OesApiRemoteCfgT) -> bool:
        """
        解析客户端配置文件

        Args:
            config_file_name (str): [配置文件路径]
            section (str): [配置区段名称]
            addr_key (str): [地址列表的配置项关键字]
            remote_cfg (OesApiRemoteCfgT): [输出远程主机配置信息]

        Returns:
            [bool]: [TRUE 成功; FALSE 失败]
        """
        subscribe_info: OesApiSubscribeInfoT = OesApiSubscribeInfoT()

        return COesApiFuncLoader().c_oes_api_parse_config_from_file(
            config_file_name, section, addr_key,
            byref(remote_cfg) if remote_cfg else None,
            byref(subscribe_info))

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def parse_addr_list_string(self, uri_list: str,
            p_out_addr_list: POINTER(OesApiAddrInfoT) = None) -> int:
        """
        解析服务器地址列表字符串
        - 待解析的地址列表可是以空格、逗号或分号分割的地址列表字符串
          - e.g. "tcp://127.0.0.1:5100, tcp://192.168.0.11:5100"
        - 同时也可以在每个地址之前, 为其指定对应的主机编号
          - e.g. "2 tcp://192.168.0.12:5100, 1 tcp://192.168.0.11:5100, 3 tcp://192.168.0.13:5100"

        Args:
            uri_list (str): [主机地址列表 (以空格、逗号或分号分割的地址列表字符串)]
            p_out_addr_list (POINTER(OesApiAddrInfoT)): [用于输出解析后的地址信息的地址信息数组]

        Returns:
            [int]: [大于等于0, 解析得到的地址数量; 小于0, 解析失败]
        """
        return COesApiFuncLoader().c_oes_api_parse_addr_list_string(
            uri_list,
            p_out_addr_list if p_out_addr_list else None,
            GENERAL_CLI_MAX_REMOTE_CNT)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_customized_ip_and_mac(self, ip_str: str, mac_str: str) -> bool:
        """
        设置客户端自定义的本地IP地址

        Args:
            ip_str (str): [点分十进制的IP地址字符串]
            mac_str (str): [MAC地址字符串 (MAC地址格式 45:38:56:89:78:5A)]

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        return COesApiFuncLoader().c_oes_api_set_customized_ip_and_mac(
            ip_str, mac_str)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_customized_ip(self, ip_str: str) -> bool:
        """
        设置客户端自定义的本地IP地址

        Args:
            ip_str (str): [点分十进制的IP地址字符串]

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        return COesApiFuncLoader().c_oes_api_set_customized_ip(ip_str)

    @spk_decorator_exception(log_error=log_error, error_no='')
    def get_customized_ip(self) -> str:
        """
        获取客户端自定义的本地IP

        Returns:
            [str]: [客户端自定义的本地IP]
        """
        return COesApiFuncLoader().c_oes_api_get_customized_ip().decode()

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_customized_mac(self, mac_str: str) -> bool:
        """
        设置客户端自定义的本地MAC地址

        Args:
            mac_str (str): [MAC地址字符串 (MAC地址格式 45:38:56:89:78:5A)]

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        return COesApiFuncLoader().c_oes_api_set_customized_mac(mac_str)

    @spk_decorator_exception(log_error=log_error, error_no='')
    def get_customized_mac(self) -> str:
        """
        获取客户端自定义的本地MAC

        Returns:
            [str]: [客户端自定义的本地MAC]
        """
        return COesApiFuncLoader().c_oes_api_get_customized_mac().decode()

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_customized_driver_id(self, driver_id: str) -> bool:
        """
        设置客户端自定义的本地设备序列号字符串

        Args:
            driver_id (str): [设备序列号字符串]

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        return COesApiFuncLoader().c_oes_api_set_customized_driver_id(driver_id)

    @spk_decorator_exception(log_error=log_error, error_no='')
    def get_customized_driver_id(self) -> str:
        """
        获取客户端自定义的本地设备序列号

        Returns:
            [str]: [客户端自定义的本地设备序列号]
        """
        return COesApiFuncLoader().c_oes_api_get_customized_driver_id().decode()

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_client_appl_name(self, client_appl_name: str) -> bool:
        """
        设置客户端的交易终端软件名称

        Args:
            client_appl_name (str): [交易终端软件名称]

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        return COesApiFuncLoader().c_oes_api_set_client_appl_name(
            client_appl_name)

    @spk_decorator_exception(log_error=log_error, error_no='')
    def get_client_appl_name(self) -> str:
        """
        获取客户端的交易终端软件名称

        Returns:
            [str]: [交易终端软件名称]
        """
        return COesApiFuncLoader().c_oes_api_get_client_appl_name().decode()

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_client_appl_version(self, client_appl_version: str) -> bool:
        """
        设置客户端的交易终端软件版本

        Args:
            client_appl_version (str): [交易终端软件版本]

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        return COesApiFuncLoader().c_oes_api_set_client_appl_version(
            client_appl_version)

    @spk_decorator_exception(log_error=log_error, error_no='')
    def get_client_appl_version(self) -> str:
        """
        获取客户端的交易终端软件版本

        Returns:
            [str]: [交易终端软件版本]
        """
        return COesApiFuncLoader().c_oes_api_get_client_appl_version().decode()

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_device_serial_no(self, device_serial_no: str) -> bool:
        """
        设置客户端的交易终端设备序列号 (macOS系统为必采项)

        Args:
            device_serial_no (str): [交易终端设备序列号]

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        return COesApiFuncLoader().c_oes_api_set_device_serial_no(
            device_serial_no)

    @spk_decorator_exception(log_error=log_error, error_no='')
    def get_device_serial_no(self) -> str:
        """
        获取客户端的交易终端设备序列号 (macOS系统为必采项)

        Returns:
            [str]: [交易终端设备序列号]
        """
        return COesApiFuncLoader().c_oes_api_get_device_serial_no().decode()

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_default_entrust_way(self, entrust_way: str) -> int:
        """
        设置客户端的默认委托方式

        Args:
            entrust_way (str): [委托方式，长度需为1]

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        b_entrust_way: bytes = entrust_way.encode()
        if len(b_entrust_way) < 1:
            return False

        return COesApiFuncLoader().c_oes_api_set_entrust_way(
            c_char(b_entrust_way))

    @spk_decorator_exception(log_error=log_error, error_no='')
    def get_default_entrust_way(self) -> str:
        """
        获取客户端默认的委托方式 (对当前进程生效)

        Returns:
            [str]: [客户端默认的委托方式 (对当前进程生效)]
        """
        return COesApiFuncLoader().c_oes_api_get_entrust_way().decode()

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def get_business_type(self, channel: OesAsyncApiChannelT = None) -> int:
        """
        返回通道对应的业务类型

        Returns:
            [int]: [通道对应的业务类型]
        """
        if channel:
            return COesApiFuncLoader().c_oes_api_get_business_type(
                channel.pSessionInfo)
        else:
            return eOesBusinessTypeT.OES_BUSINESS_TYPE_UNDEFINE

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def get_last_error(self) -> int:
        """
        返回当前线程最近一次API调用失败的错误号

        Returns:
            [int]: [错误号]
        """
        return COesApiFuncLoader().c_oes_api_get_last_error()

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_last_error(self, err_code: int) -> bool:
        """
        设置当前线程的API错误号

        Args:
            err_code (int): [错误号]

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        COesApiFuncLoader().c_oes_api_set_last_error(err_code)
        return True

    @spk_decorator_exception(log_error=log_error, error_no='')
    def get_error_msg(self, err_code: int) -> str:
        """
        返回错误号对应的错误信息

        Args:
            err_code (int): [错误号]

        Returns:
            [str]: [错误码对应的错误信息]
        """
        return COesApiFuncLoader().c_oes_api_get_error_msg(err_code).decode()
    # -------------------------
    
    
    # ===================================================================
    # Python API自定义接口函数
    # ===================================================================

    def get_default_channel(self) -> Optional[OesAsyncApiChannelT]:
        """
        返回默认委托或回报通道

        Returns:
            [OesAsyncApiChannelT]: [默认的委托或回报通道]
        """
        return self.get_default_ord_channel() or self.get_default_rpt_channel()

    def get_default_ord_channel(self) -> Optional[OesAsyncApiChannelT]:
        """
        返回默认的委托通道

        Returns:
            [OesAsyncApiChannelT]: [默认的委托通道]
        """
        if self._default_ord_channel:
            return self._default_ord_channel.contents

        if self._ord_channels:
            for tuple_value in self._ord_channels.values():
                return tuple_value[0]
        else:
            return None

    def get_default_rpt_channel(self) -> Optional[OesAsyncApiChannelT]:
        """
        返回默认的回报通道

        Returns:
            [OesAsyncApiChannelT]: [默认的回报通道]
        """
        if self._default_rpt_channel:
            return self._default_rpt_channel.contents

        if self._rpt_channels:
            for tuple_value in self._rpt_channels.values():
                return tuple_value[0]
        else:
            return None

    def set_last_cl_seq_no(self, cl_env_id: int = 0,
            last_cl_seq_no: int = 0, is_force: bool = False) -> int:
        """
        设置环境号下最近的流水号 (默认设置环境号为0的最近流水号)
        - @note 非线程安全, 客户端可根据需要, 自行实现流水号序列, 本接口仅供参考

        Args:
            cl_env_id (int): [环境号]
            last_cl_seq_no (int): [最近的流水号]
            is_force (int): [是否强制设置]
            - True, 强制设置, 不校验流水号是否倒流
            - False, 不强制设置, 流水号倒流则不更新

        Returns:
            [int]: [环境号对应的下一个有效流水号]
        """
        if cl_env_id < 0:
            cl_env_id = 0

        if last_cl_seq_no < 0:
            last_cl_seq_no = 0

        if is_force:
            # 强制更新流水号
            self._cl_seq_nos[cl_env_id] = last_cl_seq_no
        else:
            if self._cl_seq_nos.get(cl_env_id, -1) == -1:
                # 环境号不存在
                self._cl_seq_nos[cl_env_id] = last_cl_seq_no

            elif self._cl_seq_nos[cl_env_id] < last_cl_seq_no:
                # 环境号当前流水号小于待设置的流水号, 更新
                self._cl_seq_nos[cl_env_id] = last_cl_seq_no

            else:
                # 环境号当前流水号大于等于待设置的流水号, 不更新
                pass

        return self._cl_seq_nos[cl_env_id]

    def get_next_cl_seq_no(self, cl_env_id: int = 0) -> int:
        """
        获取环境号对应的下一个有效流水号 (默认获取环境号为0的流水号)
        - @note 非线程安全, 客户端可根据需要, 自行实现流水号序列, 本接口仅供参考

        Args:
            cl_env_id (int): [环境号]

        Returns:
            [int]: [环境号对应的下一个有效流水号]
        """
        if cl_env_id < 0:
            cl_env_id = 0

        if self._cl_seq_nos.get(cl_env_id, -1) == -1:
            self._cl_seq_nos[cl_env_id] = 1
        else:
            self._cl_seq_nos[cl_env_id] += 1

        return self._cl_seq_nos[cl_env_id]
    # -------------------------


    # ===================================================================
    # Python API自定义私有函数 (内部使用, 不对外开放)
    # ===================================================================

    def __add_channel_base_impl(self,
            is_add_from_file: bool = True,
            is_add_ord_channel: bool = True,
            channel_tag: str = "",
            user_info: Any = "",
            oes_client_spi: Optional[OesClientSpi] = None,
            copy_args: bool = True,

            remote_cfg: OesApiRemoteCfgT = None,

            config_file: str = "",
            config_section: str = OESAPI_CFG_DEFAULT_SECTION,
            addr_key: str = OESAPI_CFG_DEFAULT_KEY_ORD_ADDR) -> OesAsyncApiChannelT:
        """
        添加通道的基础实现

        Args:
            is_add_from_file (bool): [是否为 "从配置文件中加载并添加通道配置信息"]
            is_add_ord_channel (bool): [是否为添加委托通道 (True: 委托通道; False: 回报通道)]
            channel_tag (str): [通道配置信息的自定义标签 (可以为空)]
            user_info (Any): [用户回调参数]
            oes_client_spi (OesClientSpi): [委托或回报通道消息的处理函数类].
            - Defaults to None. 此时默认使用self.oes_spi
            copy_args (bool): [是否复制服务端返回的行情数据].
            - Defaults to True
            - 可手动设置成False, 会提升吞吐和降低时延，但是行情数据需要立即保存起来, 否则后期使用会因异步队列数据覆盖而无法访问的风险

            remote_cfg (OesApiRemoteCfgT): [待添加的通道配置信息 (不可为空)].
            - 仅适用于is_add_from_file=False有效

            config_file (OesApiRemoteCfgT): [待添加的通道配置信息 (不可为空)].
            - 仅适用于is_add_from_file=True有效
            config_section (OesApiRemoteCfgT): [待添加的通道配置信息 (不可为空)].
            - 仅适用于is_add_from_file=True有效
            addr_key (OesApiRemoteCfgT): [待添加的通道配置信息 (不可为空)].
            - 仅适用于is_add_from_file=True有效

        Returns:
            [OesAsyncApiChannelT]: [通道信息，请勿对其进行任何修改赋值操作]
        """
        if self._oes_api_started:
            raise Exception("需在调用start前添加通道信息! "
                "oes_api_started[{}]".format(self._oes_api_started))

        if not channel_tag or channel_tag.strip() == '' :
            channel_tag = self.__get_auto_allocated_channel_tag(
                is_ord_channel=is_add_ord_channel)

        if len(channel_tag) >= GENERAL_CLI_MAX_NAME_LEN:
            # @note 需注意分配的通道标签长度不能超过32位, 否则截取后32位 (正常不会进入该分支)
            channel_tag = \
                channel_tag[len(channel_tag) - GENERAL_CLI_MAX_NAME_LEN + 1:]

        if channel_tag in self._ord_channels.keys() \
            or channel_tag in self._rpt_channels.keys():
            raise Exception("通道标签已存在, 重复添加了委托或回报通道? "
                "channel_tag[{}], ord_channels[{}], rpt_channels[{}]".format(
                channel_tag,
                self._ord_channels.keys(),
                self._rpt_channels.keys()))

        if oes_client_spi is None:
            if self.oes_spi is None:
                raise Exception("尚未给异步API注册有效的回调类实例!")
            else:
                oes_client_spi = self.oes_spi

        if not isinstance(oes_client_spi, OesClientSpi):
            raise Exception("非法的回调类类型! spi_type[{}]".format(
                type(oes_client_spi)))

        msg_dispatcher: OesMsgDispatcher = \
            OesMsgDispatcher(oes_client_spi, copy_args)
        self._oes_msg_dispatchers.append(msg_dispatcher)

        if is_add_ord_channel is True:
            channel_type = eOesApiChannelTypeT.OESAPI_CHANNEL_TYPE_ORDER
            msg_dispatcher_xxx_handle_msg = msg_dispatcher.handle_report_msg
            msg_dispatcher_xxx_on_connect = msg_dispatcher.on_ord_connect
            msg_dispatcher_xxx_on_connect_failed = msg_dispatcher.on_ord_connect_failed
            msg_dispatcher_xxx_on_disconnect = msg_dispatcher.on_ord_disconnect

        else:
            channel_type = eOesApiChannelTypeT.OESAPI_CHANNEL_TYPE_REPORT
            msg_dispatcher_xxx_handle_msg = msg_dispatcher.handle_report_msg
            msg_dispatcher_xxx_on_connect = msg_dispatcher.on_rpt_connect
            msg_dispatcher_xxx_on_connect_failed = msg_dispatcher.on_rpt_connect_failed
            msg_dispatcher_xxx_on_disconnect = msg_dispatcher.on_rpt_disconnect

        if is_add_from_file:
            assert remote_cfg is None

            if not config_file:
                config_file = self._config_file

            p_channel: _Pointer = \
                COesApiFuncLoader().c_oes_async_api_add_channel_from_file(
                    self._oes_api_context, channel_type, channel_tag,
                    config_file, config_section, addr_key,
                    msg_dispatcher_xxx_handle_msg(user_info), VOID_NULLPTR,
                    msg_dispatcher_xxx_on_connect(user_info), VOID_NULLPTR,
                    msg_dispatcher_xxx_on_disconnect(user_info), VOID_NULLPTR)

        else:
            assert config_file == "" and config_section == "" and addr_key == ""

            if not remote_cfg:
                raise Exception("待添加的通道配置信息, 不可为空! "
                    "remote_cfg[{}]".format(remote_cfg))

            p_channel: _Pointer = \
                COesApiFuncLoader().c_oes_async_api_add_channel(
                    self._oes_api_context, channel_type, channel_tag,
                    byref(remote_cfg) if remote_cfg else None, None,
                    msg_dispatcher_xxx_handle_msg(user_info), VOID_NULLPTR,
                    msg_dispatcher_xxx_on_connect(user_info), VOID_NULLPTR,
                    msg_dispatcher_xxx_on_disconnect(user_info), VOID_NULLPTR)

        if not p_channel:
            log_error("委托或回报通道添加失败! channel_tag[{}]".format(channel_tag))
            raise Exception("委托或回报通道添加失败!")
        else:
            # 设置连接失败时的回调函数
            COesApiFuncLoader().c_oes_async_api_set_on_connect_failed(
                p_channel,
                msg_dispatcher_xxx_on_connect_failed(user_info),
                VOID_NULLPTR)

        # @note 基础类型无法修改, 故特殊判断, 后续优化
        if is_add_ord_channel:
            if not self._default_ord_channel:
                self._default_ord_channel = p_channel

            # 将通道与消息分发器一对一绑定
            self._ord_channels[channel_tag] = \
                (p_channel.contents, msg_dispatcher)
        else:
            if not self._default_rpt_channel:
                self._default_rpt_channel = p_channel

            # 将通道与消息分发器一对一绑定
            self._rpt_channels[channel_tag] = \
                (p_channel.contents, msg_dispatcher)

        return p_channel.contents

    def __get_oes_msg_dispatcher_by_channel(self,
            channel: OesAsyncApiChannelT = None) -> OesMsgDispatcher:
        """
        获取通道对应的OES消息分发器 (内部使用, 暂不对外开放)

        Args:
            channel (OesAsyncApiChannelT): [查询通道]

        Returns:
            [OesMsgDispatcher]: [消息分发器]
        """
        if channel is None:
            channel = self.get_default_channel()

        channel_tag = channel.pChannelCfg.contents.channelTag.decode()

        # 分别从委托和回报通道获取分发器
        channel_dispatcher: tuple = \
            self._ord_channels.get(channel_tag, None) \
                or self._rpt_channels.get(channel_tag, None)

        if channel_dispatcher is None:
            raise Exception("Invalid params! channel_tag[{}], "
                "ord_channels[{}], rpt_channels[{}]".format(
                channel_tag, self._ord_channels, self._rpt_channels))

        # 0号元素: OesAsyncApiChannelT
        # 1号元素: OesMsgDispatcher
        assert len(channel_dispatcher) == 2
        oes_msg_dispatcher: OesMsgDispatcher = channel_dispatcher[1]
        if oes_msg_dispatcher is None:
            raise Exception("Invalid params! channel[{}]".format(
                channel))
        else:
            assert oes_msg_dispatcher.get_spi() is not None

        return oes_msg_dispatcher

    def __get_auto_allocated_channel_tag(self,
            is_ord_channel: bool = True) -> str:
        """
        获取自动分配的通道标签 (内部使用, 暂不对外开放)
        - 外部添加通道时, 未指定标签, API内部会自动分配

        Args:
            is_ord_channel (bool): [是否为委托通道]
        Returns:
            [str]: [自动分配的通道标签]
        """
        self.current_channel_no += 1

        if is_ord_channel is True:
            channel_tag = f"__ord_channel@0x{self.current_channel_no:0x}"
        else:
            channel_tag = f"__rpt_channel@0x{self.current_channel_no:0x}"

        if len(channel_tag) >= GENERAL_CLI_MAX_NAME_LEN:
            # @note 需注意分配的通道标签长度不能超过32位, 否则截取后32位 (正常不会进入该分支)
            channel_tag = \
                channel_tag[len(channel_tag) - GENERAL_CLI_MAX_NAME_LEN + 1:]

        return channel_tag
    # -------------------------
