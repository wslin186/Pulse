# -*- coding: utf-8 -*-
"""
capi函数加载相关
"""

from ctypes import (
    c_int8, c_uint8, c_int, c_int32, c_uint32, c_int64, c_char, c_char_p,
    c_void_p, POINTER, CFUNCTYPE, Structure
)

from vendor.trade_api.model import (
    # spk_util.py
    SingletonType, CCharP, SMsgHeadT,
    OesApiRemoteCfgT, OesApiAddrInfoT,
    OesAsyncApiChannelT, OesAsyncApiContextT, OesAsyncApiChannelCfgT,
    CApiFuncLoader,

    # oes_base_constants.py

    # oes_base_model_credit.py

    # oes_base_model_option_.py

    # oes_base_model.py
    OesOrdReqT, OesOrdCancelReqT, OesFundTrsfReqT,
    OesCashAssetItemT,

    # oes_qry_packets.py
    OesClientOverviewT, OesCounterCashItemT, OesBrokerParamsInfoT,
    OesQryCursorT, OesQryCustFilterT, OesQryInvAcctFilterT,
    OesQryCashAssetFilterT,  OesQryFundTransferSerialFilterT,
    OesQryStkHoldingFilterT, OesQryOrdFilterT,OesQryTrdFilterT,
    OesQryStockFilterT, OesQryIssueFilterT,
    OesQryEtfComponentFilterT, OesQryEtfFilterT,
    OesQryCommissionRateFilterT, OesQryLotWinningFilterT,
    OesQryMarketStateFilterT, OesQryNotifyInfoFilterT,

    # oes_qry_packets_credit.py
    OesCrdCollateralTransferOutMaxQtyItemT,
    OesCrdDrawableBalanceItemT,
    OesQryCrdCashRepayFilterT, OesQryCrdCreditAssetFilterT,
    OesQryCrdDebtContractFilterT, OesQryCrdDebtJournalFilterT,
    OesQryCrdExcessStockFilterT, OesQryCrdInterestRateFilterT,
    OesQryCrdUnderlyingInfoFilterT, OesQryCrdSecurityDebtStatsFilterT,
    OesQryCrdSecurityPositionFilterT, OesQryCrdCashPositionFilterT,

    # oes_qry_packets_option.py
    OesQryOptionFilterT, OesQryOptHoldingFilterT,
    OesQryOptPositionLimitFilterT, OesQryOptPurchaseLimitFilterT,
    OesQryOptUnderlyingHoldingFilterT, OesQryOptExerciseAssignFilterT,

    # oes_packets.py
    OesRspMsgBodyT, OesApiSubscribeInfoT,
    OesChangePasswordReqT, OesOptSettlementConfirmReqT,
)


# ===================================================================
# 结构体定义
# ===================================================================

class OesAsyncApiContextParamsT(Structure):
    """
    OES异步API的上下文环境的创建参数 (仅做为 CreateContext 接口的参数使用)
    """
    _fields_ = (
        # 异步队列的大小
        ("asyncQueueSize", c_int32),

        # 是否优先使用大页内存来创建异步队列
        ("isHugepageAble", c_uint8),
        # 是否启动独立的回调线程来执行回调处理 (否则将直接在通信线程下执行回调处理)
        ("isAsyncCallbackAble", c_uint8),
        # 是否启动独立的连接管理线程来执行连接处理和OnConnect回调处理 (当通道数量大于1时建议开启, 否则将直接在通信线程下执行)
        ("isAsyncConnectAble", c_uint8),
        # 是否使用忙等待模式 (TRUE:延迟更低但CPU会被100%占用; FALSE:延迟和CPU使用率相对均衡)
        ("isBusyPollAble", c_uint8),
        # 是否在启动前预创建并校验所有的连接
        ("isPreconnectAble", c_uint8),
        # 是否启用内置的查询通道 (TRUE:启动异步API时自动创建内置的查询通道; FALSE:不创建内置的查询通道)
        ("isBuiltinQueryable", c_uint8),

        # Onload 加速标志
        # - 0: 未启用 onload 加速
        # - 1: 已启用 onload 加速
        # - 2: 自动管理 onload 栈
        # - 3: 自动管理 onload 栈, 且按环境号分配委托队列的 onload 栈
        ("onloadFlag", c_uint8),
        # 为保证64位对齐而设
        ("__filler1", c_uint8 * 5),
    )
# -------------------------


# ===================================================================
# 回调函数的函数原型定义
# ===================================================================

# 对查询结果进行处理的回调函数的函数原型定义
F_OESAPI_ASYNC_ON_QRY_MSG_T = CFUNCTYPE(
    c_int32,
    c_void_p,
    POINTER(SMsgHeadT),
    c_void_p,
    POINTER(OesQryCursorT),
    c_void_p
)

# 对接收到的应答或回报消息进行处理的回调函数的函数原型定义
F_OESAPI_ASYNC_ON_RPT_MSG_T = CFUNCTYPE(
    c_int32,
    c_void_p,
    POINTER(SMsgHeadT),
    POINTER(OesRspMsgBodyT),
    c_void_p
)

#  异步API线程连接或重新连接完成后的回调函数的函数原型定义
F_OESAPI_ASYNC_ON_CONNECT_T = CFUNCTYPE(
    c_int32,
    POINTER(OesAsyncApiChannelT),
    c_void_p
)

#  异步API线程连接断开后的回调函数的函数原型定义
F_OESAPI_ASYNC_ON_DISCONNECT_T = CFUNCTYPE(
    c_int32,
    POINTER(OesAsyncApiChannelT),
    c_void_p
)

# 异步API遍历所有的连接通道信息的回调函数的函数原型定义
F_OESAPI_ASYNC_FOREACH_CHANNEL_T = CFUNCTYPE(
    c_int32,
    POINTER(OesAsyncApiChannelT),
    c_void_p
)
# -------------------------


class COesApiFuncLoader(CApiFuncLoader, metaclass=SingletonType):
    """
    交易capi动态库函数加载
    """

    def __init__(self) -> None:
        super().__init__()

        # ===================================================================
        # OES异步API接口函数封装 (上下文管理接口)
        # ===================================================================

        # 创建异步API的运行时环境 (通过配置文件和默认的配置区段加载相关配置参数)
        self.c_oes_async_api_create_context = self.c_api_dll.OesAsyncApi_CreateContext
        self.c_oes_async_api_create_context.argtypes = [CCharP]
        self.c_oes_async_api_create_context.restype = POINTER(OesAsyncApiContextT)

        # 创建异步API的运行时环境 (通过配置文件和指定的配置区段加载相关配置参数)
        self.c_oes_async_api_create_context2 = self.c_api_dll.OesAsyncApi_CreateContext2
        self.c_oes_async_api_create_context2.restype = POINTER(OesAsyncApiContextT)
        self.c_oes_async_api_create_context2.argtypes = [CCharP, CCharP, CCharP, CCharP]

        # 创建异步API的运行时环境 (仅通过函数参数指定必要的配置参数)
        self.c_oes_async_api_create_context_simple = self.c_api_dll.OesAsyncApi_CreateContextSimple
        self.c_oes_async_api_create_context_simple.restype = POINTER(OesAsyncApiContextT)
        self.c_oes_async_api_create_context_simple.argtypes = [CCharP, CCharP, c_int]

        # 创建异步API的运行时环境 (仅通过函数参数指定必要的配置参数)
        self.c_oes_async_api_create_context_simple2 = self.c_api_dll.OesAsyncApi_CreateContextSimple2
        self.c_oes_async_api_create_context_simple2.restype = POINTER(OesAsyncApiContextT)
        self.c_oes_async_api_create_context_simple2.argtypes = [
            CCharP, CCharP, POINTER(OesAsyncApiContextParamsT)
        ]

        # 释放异步API的运行时环境
        self.c_oes_async_api_release_context = self.c_api_dll.OesAsyncApi_ReleaseContext
        self.c_oes_async_api_release_context.restype = None
        self.c_oes_async_api_release_context.argtypes = [POINTER(OesAsyncApiContextT)]

        # 启动异步API线程
        self.c_oes_async_api_start = self.c_api_dll.OesAsyncApi_Start
        self.c_oes_async_api_start.restype = c_int
        self.c_oes_async_api_start.argtypes = [POINTER(OesAsyncApiContextT)]

        # 终止异步API线程
        self.c_oes_async_api_stop = self.c_api_dll.OesAsyncApi_Stop
        self.c_oes_async_api_stop.restype = None
        self.c_oes_async_api_stop.argtypes = [POINTER(OesAsyncApiContextT)]

        # 返回异步API的通信线程是否正在运行过程中
        self.c_oes_async_api_is_running = self.c_api_dll.OesAsyncApi_IsRunning
        self.c_oes_async_api_is_running.restype = c_int
        self.c_oes_async_api_is_running.argtypes = [POINTER(OesAsyncApiContextT)]

        # 返回异步API相关的所有线程是否都已经安全退出 (或尚未运行)
        self.c_oes_async_api_is_all_terminated = self.c_api_dll.OesAsyncApi_IsAllTerminated
        self.c_oes_async_api_is_all_terminated.restype = c_int
        self.c_oes_async_api_is_all_terminated.argtypes = [POINTER(OesAsyncApiContextT)]

        # 返回异步API累计已提取和处理过的行情消息数量
        self.c_oes_async_api_get_total_picked = self.c_api_dll.OesAsyncApi_GetTotalPicked
        self.c_oes_async_api_get_total_picked.restype = c_int64
        self.c_oes_async_api_get_total_picked.argtypes = [POINTER(OesAsyncApiContextT)]

        # 返回异步I/O线程累计已提取和处理过的消息数量
        self.c_oes_async_api_get_total_io_picked = self.c_api_dll.OesAsyncApi_GetTotalIoPicked
        self.c_oes_async_api_get_total_io_picked.restype = c_int64
        self.c_oes_async_api_get_total_io_picked.argtypes = [POINTER(OesAsyncApiContextT)]

        # 返回异步API累计已入队的消息数量
        self.c_oes_async_api_get_async_queue_total_count = self.c_api_dll.OesAsyncApi_GetAsyncQueueTotalCount
        self.c_oes_async_api_get_async_queue_total_count.restype = c_int64
        self.c_oes_async_api_get_async_queue_total_count.argtypes = [POINTER(OesAsyncApiContextT)]

        # 返回队列中尚未被处理的剩余数据数量
        self.c_oes_async_api_get_async_queue_remaining_count = self.c_api_dll.OesAsyncApi_GetAsyncQueueRemainingCount
        self.c_oes_async_api_get_async_queue_remaining_count.restype = c_int64
        self.c_oes_async_api_get_async_queue_remaining_count.argtypes = [POINTER(OesAsyncApiContextT)]
        # -------------------------


        # ===================================================================
        # OES异步API接口函数封装 (通道管理接口)
        # ===================================================================

        # 返回通道数量 (通道配置信息数量)
        self.c_oes_async_api_get_channel_count = self.c_api_dll.OesAsyncApi_GetChannelCount
        self.c_oes_async_api_get_channel_count.restype = c_int32
        self.c_oes_async_api_get_channel_count.argtypes = [POINTER(OesAsyncApiContextT)]

        # 返回当前已连接的通道数量
        self.c_oes_async_api_get_connected_channel_count = self.c_api_dll.OesAsyncApi_GetConnectedChannelCount
        self.c_oes_async_api_get_connected_channel_count.restype = c_int32
        self.c_oes_async_api_get_connected_channel_count.argtypes = [POINTER(OesAsyncApiContextT)]

        # 添加通道配置信息
        self.c_oes_async_api_add_channel = self.c_api_dll.OesAsyncApi_AddChannel
        self.c_oes_async_api_add_channel.restype = POINTER(OesAsyncApiChannelT)
        self.c_oes_async_api_add_channel.argtypes = [
            POINTER(OesAsyncApiContextT),
            c_int, CCharP,
            POINTER(OesApiRemoteCfgT),
            POINTER(OesApiSubscribeInfoT),
            F_OESAPI_ASYNC_ON_RPT_MSG_T, c_void_p,
            F_OESAPI_ASYNC_ON_CONNECT_T, c_void_p,
            F_OESAPI_ASYNC_ON_DISCONNECT_T, c_void_p
        ]

        # 从配置文件中加载并添加通道配置信息
        self.c_oes_async_api_add_channel_from_file = self.c_api_dll.OesAsyncApi_AddChannelFromFile
        self.c_oes_async_api_add_channel_from_file.restype = POINTER(OesAsyncApiChannelT)
        self.c_oes_async_api_add_channel_from_file.argtypes = [
            POINTER(OesAsyncApiContextT),
            c_int, CCharP, CCharP, CCharP, CCharP,
            F_OESAPI_ASYNC_ON_RPT_MSG_T, c_void_p,
            F_OESAPI_ASYNC_ON_CONNECT_T, c_void_p,
            F_OESAPI_ASYNC_ON_DISCONNECT_T, c_void_p
        ]

        # 返回顺序号对应的连接通道信息
        self.c_oes_async_api_get_channel = self.c_api_dll.OesAsyncApi_GetChannel
        self.c_oes_async_api_get_channel.restype = POINTER(OesAsyncApiChannelT)
        self.c_oes_async_api_get_channel.argtypes = [c_void_p, c_int32]

        # 返回标签对应的连接通道信息
        self.c_oes_async_api_get_channel_by_tag = self.c_api_dll.OesAsyncApi_GetChannelByTag
        self.c_oes_async_api_get_channel_by_tag.restype = POINTER(OesAsyncApiChannelT)
        self.c_oes_async_api_get_channel_by_tag.argtypes = [c_void_p, c_int32, CCharP]

        # 返回会话信息对应的异步API连接通道信息 (Python API内部使用, 暂不对外开放)
        self.c_oes_async_api_get_channel_by_session = self.c_api_dll.OesAsyncApi_GetChannelBySession
        self.c_oes_async_api_get_channel_by_session.restype = POINTER(OesAsyncApiChannelT)
        self.c_oes_async_api_get_channel_by_session.argtypes = [c_void_p]

        # 遍历所有的连接通道信息并执行回调函数
        self.c_oes_async_api_foreach_channel = self.c_api_dll.OesAsyncApi_ForeachChannel
        self.c_oes_async_api_foreach_channel.restype = POINTER(c_int32)
        self.c_oes_async_api_foreach_channel.argtypes = [
            POINTER(OesAsyncApiContextT),
            F_OESAPI_ASYNC_FOREACH_CHANNEL_T, c_void_p
        ]
        # 遍历所有的连接通道信息并执行回调函数 (暂不对接, 与OesAsyncApi_ForeachChannel区别在于自定义参数个数)
        # OesAsyncApi_ForeachChannel2
        # 遍历所有的连接通道信息并执行回调函数 (暂不对接, 与OesAsyncApi_ForeachChannel区别在于自定义参数个数)
        # OesAsyncApi_ForeachChannel3

        # 返回通道是否已连接就绪
        self.c_oes_async_api_is_channel_connected = self.c_api_dll.OesAsyncApi_IsChannelConnected
        self.c_oes_async_api_is_channel_connected.restype = c_int
        self.c_oes_async_api_is_channel_connected.argtypes = [POINTER(OesAsyncApiChannelT)]

        # 返回通道对应的配置信息
        self.c_oes_async_api_get_channel_cfg = self.c_api_dll.OesAsyncApi_GetChannelCfg
        self.c_oes_async_api_get_channel_cfg.restype = POINTER(OesAsyncApiChannelCfgT)
        self.c_oes_async_api_get_channel_cfg.argtypes = [POINTER(OesAsyncApiChannelT)]

        # 返回通道对应的行情订阅配置信息
        self.c_oes_async_api_get_channel_subscribe_cfg = self.c_api_dll.OesAsyncApi_GetChannelSubscribeCfg
        self.c_oes_async_api_get_channel_subscribe_cfg.restype = POINTER(OesApiSubscribeInfoT)
        self.c_oes_async_api_get_channel_subscribe_cfg.argtypes = [POINTER(OesAsyncApiChannelT)]

        # 设置连接或重新连接完成后的回调函数 (Python API内部使用, 暂不对外开放)
        self.c_oes_async_api_set_on_connect = self.c_api_dll.OesAsyncApi_SetOnConnect
        self.c_oes_async_api_set_on_connect.restype = c_int
        self.c_oes_async_api_set_on_connect.argtypes = [
            POINTER(OesAsyncApiChannelT),
            F_OESAPI_ASYNC_ON_CONNECT_T,
            c_void_p
        ]

        # 返回连接或重新连接完成后的回调函数 (Python API内部使用, 暂不对外开放)
        self.c_oes_async_api_get_on_connect = self.c_api_dll.OesAsyncApi_GetOnConnect
        self.c_oes_async_api_get_on_connect.restype = F_OESAPI_ASYNC_ON_CONNECT_T
        self.c_oes_async_api_get_on_connect.argtypes = [POINTER(OesAsyncApiChannelT)]

        # 设置连接断开后的回调函数 (Python API内部使用, 暂不对外开放)
        self.c_oes_async_api_set_on_disconnect = self.c_api_dll.OesAsyncApi_SetOnDisconnect
        self.c_oes_async_api_set_on_disconnect.restype = c_int
        self.c_oes_async_api_set_on_disconnect.argtypes = [
            POINTER(OesAsyncApiChannelT),
            F_OESAPI_ASYNC_ON_DISCONNECT_T,
            c_void_p
        ]

        # 返回连接断开后的回调函数 (Python API内部使用, 暂不对外开放)
        self.c_oes_async_api_get_on_disconnect = self.c_api_dll.OesAsyncApi_GetOnDisconnect
        self.c_oes_async_api_get_on_disconnect.restype = F_OESAPI_ASYNC_ON_DISCONNECT_T
        self.c_oes_async_api_get_on_disconnect.argtypes = [POINTER(OesAsyncApiChannelT)]

        # 设置连接失败时的回调函数 (Python API内部使用, 暂不对外开放)
        self.c_oes_async_api_set_on_connect_failed = self.c_api_dll.OesAsyncApi_SetOnConnectFailed
        self.c_oes_async_api_set_on_connect_failed.restype = c_int
        self.c_oes_async_api_set_on_connect_failed.argtypes = [
            POINTER(OesAsyncApiChannelT),
            F_OESAPI_ASYNC_ON_DISCONNECT_T,
            c_void_p
        ]

        # 返回连接失败时的回调函数 (Python API内部使用, 暂不对外开放)
        self.c_oes_async_api_get_on_connect_failed = self.c_api_dll.OesAsyncApi_GetOnConnectFailed
        self.c_oes_async_api_get_on_connect_failed.restype = F_OESAPI_ASYNC_ON_DISCONNECT_T
        self.c_oes_async_api_get_on_connect_failed.argtypes = [POINTER(OesAsyncApiChannelT)]

        # 注册和连接通道有共生关系的会话信息 (当连接通道断开后将自动触发有共生关系的会话信息断开)
        self.c_oes_async_api_register_symbiotic_session = self.c_api_dll.OesAsyncApi_RegisterSymbioticSession
        self.c_oes_async_api_register_symbiotic_session.restype = c_int
        self.c_oes_async_api_register_symbiotic_session.argtypes = [
            POINTER(OesAsyncApiChannelT), c_void_p
        ]
        # -------------------------


        # ===================================================================
        # 委托申报接口
        # ===================================================================

        # 发送委托申报请求
        self.c_oes_async_api_send_order = self.c_api_dll.OesAsyncApi_SendOrderReq
        self.c_oes_async_api_send_order.restype = c_int32
        self.c_oes_async_api_send_order.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesOrdReqT)
        ]

        # 发送撤单请求
        self.c_oes_async_api_send_cancel_order = self.c_api_dll.OesAsyncApi_SendOrderCancelReq
        self.c_oes_async_api_send_cancel_order.restype = c_int32
        self.c_oes_async_api_send_cancel_order.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesOrdCancelReqT)
        ]

        # 批量发送多条委托请求
        self.c_oes_async_api_send_batch_orders = self.c_api_dll.OesAsyncApi_SendBatchOrdersReq
        self.c_oes_async_api_send_batch_orders.restype = c_int32
        self.c_oes_async_api_send_batch_orders.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(POINTER(OesOrdReqT)),
            c_int32
        ]

        # 发送出入金委托请求
        self.c_oes_async_api_send_fund_transfer = self.c_api_dll.OesAsyncApi_SendFundTransferReq
        self.c_oes_async_api_send_fund_transfer.restype = c_int32
        self.c_oes_async_api_send_fund_transfer.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesFundTrsfReqT)
        ]
        # -------------------------


        # ===================================================================
        # 融资融券业务特有的委托接口
        # ===================================================================

        # 发送可以指定待归还合约编号的融资融券负债归还请求
        self.c_oes_async_api_send_credit_repay_req = self.c_api_dll.OesAsyncApi_SendCreditRepayReq
        self.c_oes_async_api_send_credit_repay_req.restype = c_int32
        self.c_oes_async_api_send_credit_repay_req.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesOrdReqT),
            c_int, CCharP
        ]

        # 发送直接还款(现金还款)请求
        self.c_oes_async_api_send_credit_cash_repay_req = self.c_api_dll.OesAsyncApi_SendCreditCashRepayReq
        self.c_oes_async_api_send_credit_cash_repay_req.restype = c_int32
        self.c_oes_async_api_send_credit_cash_repay_req.argtypes = [
            POINTER(OesAsyncApiChannelT),
            c_int32, c_int64, c_int, CCharP, c_void_p
        ]
        # -------------------------


        # ===================================================================
        # 期权业务特有的委托接口
        # ===================================================================

        # 期权账户结算单确认
        # 结算单确认请求将通过委托通道发送到OES服务器, 处理结果将通过回报数据返回
        self.c_oes_async_api_send_opt_settlement_confirm_req = self.c_api_dll.OesAsyncApi_SendOptSettlementConfirmReq
        self.c_oes_async_api_send_opt_settlement_confirm_req.restype = c_int32
        self.c_oes_async_api_send_opt_settlement_confirm_req.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesOptSettlementConfirmReqT)
        ]
        # -------------------------


        # ===================================================================
        # OES异步API接口函数封装 (密码修改接口函数声明)
        # ===================================================================

        # 发送密码修改请求(修改客户端登录密码)
        # 密码修改请求通过查询通道发送到MDS服务器, 并采用请求 / 应答的方式直接返回处理结果
        self.c_oes_async_api_send_change_password_req = self.c_api_dll.OesAsyncApi_SendChangePasswordReq
        self.c_oes_async_api_send_change_password_req.restype = c_int32
        self.c_oes_async_api_send_change_password_req.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesChangePasswordReqT)
        ]
        # -------------------------


        # ===================================================================
        # 会话管理接口
        # ===================================================================

        # 发送回报同步消息 (仅适用于回报通道)
        self.c_oes_async_api_send_report_synchronization = self.c_api_dll.OesAsyncApi_SendReportSynchronization
        self.c_oes_async_api_send_report_synchronization.restype = c_int
        self.c_oes_async_api_send_report_synchronization.argtypes = [
            POINTER(OesAsyncApiChannelT), c_int8, c_int32, c_int64
        ]

        # 发送心跳消息
        self.c_oes_async_api_send_heart_beat = self.c_api_dll.OesAsyncApi_SendHeartbeat
        self.c_oes_async_api_send_heart_beat.restype = c_int
        self.c_oes_async_api_send_heart_beat.argtypes = [POINTER(OesAsyncApiChannelT)]

        # 发送测试请求消息
        self.c_oes_async_api_send_test_req = self.c_api_dll.OesAsyncApi_SendTestReq
        self.c_oes_async_api_send_test_req.restype = c_int
        self.c_oes_async_api_send_test_req.argtypes = [
            POINTER(OesAsyncApiChannelT), CCharP, c_int32
        ]

        # 连接完成后处理的默认实现
        # - 对于委托通道, 将输出连接成功的日志信息
        # - 对于回报通道, 将执行默认的回报订阅处理
        self.c_oes_async_api_default_on_connect = self.c_api_dll.OesAsyncApi_DefaultOnConnect
        self.c_oes_async_api_default_on_connect.restype = c_int32
        self.c_oes_async_api_default_on_connect.argtypes = [
            POINTER(OesAsyncApiChannelT), c_void_p
        ]

        # 连接完成后处理的默认实现(不订阅任何回报数据)
        # - 对于委托通道, 将输出连接成功的日志信息
        # - 对于回报通道, 将执行空的回报订阅处理(不订阅任何回报数据)
        self.c_oes_async_api_subscribe_nothing_on_connect = self.c_api_dll.OesAsyncApi_SubscribeNothingOnConnect
        self.c_oes_async_api_subscribe_nothing_on_connect.restype = c_int32
        self.c_oes_async_api_subscribe_nothing_on_connect.argtypes = [
            POINTER(OesAsyncApiChannelT), c_void_p
        ]
        # -------------------------


        # ===================================================================
        # OES异步API接口函数封装 (辅助的配置管理接口)
        # ===================================================================

        # 从配置文件中加载异步API运行参数
        # OesAsyncApi_LoadContextParams

        # 从配置文件中加载CPU亲和性配置
        # OesAsyncApi_LoadCpusetCfg

        # 从配置文件中加载CPU亲和性配置 (额外增加对连接管理线程的支持)
        # OesAsyncApi_LoadCpusetCfg2

        # 设置通信线程的CPU亲和性配置
        # OesAsyncApi_SetCommunicationCpusetCfg

        # 返回通信线程的CPU亲和性配置信息
        # OesAsyncApi_GetCommunicationCpusetCfg

        # 设置异步回调线程的CPU亲和性配置
        # OesAsyncApi_SetCallbackThreadCpusetCfg

        # 返回异步回调线程的CPU亲和性配置信息
        # OesAsyncApi_GetCallbackThreadCpusetCfg

        # 设置连接管理线程的CPU亲和性配置
        # OesAsyncApi_SetConnectThreadCpusetCfg

        # 返回连接管理线程的CPU亲和性配置信息
        # OesAsyncApi_GetConnectThreadCpusetCfg

        # 设置异步I/O线程的CPU亲和性配置
        # OesAsyncApi_SetIoThreadCpusetCfg

        # 返回异步I/O线程的CPU亲和性配置信息
        # OesAsyncApi_GetIoThreadCpusetCfg

        # 设置是否在启动前预创建并校验所有的连接
        self.c_oes_async_api_set_preconnect_able = self.c_api_dll.OesAsyncApi_SetPreconnectAble
        self.c_oes_async_api_set_preconnect_able.restype = c_int
        self.c_oes_async_api_set_preconnect_able.argtypes = [
            POINTER(OesAsyncApiContextT), c_int
        ]

        # 返回是否在启动前预创建并校验所有的连接
        self.c_oes_async_api_is_preconnect_able = self.c_api_dll.OesAsyncApi_IsPreconnectAble
        self.c_oes_async_api_is_preconnect_able.restype = c_int
        self.c_oes_async_api_is_preconnect_able.argtypes = [POINTER(OesAsyncApiContextT)]

        # 设置是否接管启动线程
        # OesAsyncApi_SetTakeoverStartThreadFlag

        # 返回是否接管启动线程
        # OesAsyncApi_GetTakeoverStartThreadFlag

        # 设置是否启动独立的回调线程来执行回调处理
        self.c_oes_async_api_set_async_callback_able = self.c_api_dll.OesAsyncApi_SetAsyncCallbackAble
        self.c_oes_async_api_set_async_callback_able.restype = c_int
        self.c_oes_async_api_set_async_callback_able.argtypes = [
            POINTER(OesAsyncApiContextT), c_int
        ]

        # 返回是否启动独立的回调线程来执行回调处理
        self.c_oes_async_api_is_async_callback_able = self.c_api_dll.OesAsyncApi_IsAsyncCallbackAble
        self.c_oes_async_api_is_async_callback_able.restype = c_int
        self.c_oes_async_api_is_async_callback_able.argtypes = [POINTER(OesAsyncApiContextT)]

        # 设置是否启动独立的连接管理线程来执行连接处理和OnConnect回调处理
        # OesAsyncApi_SetAsyncConnectAble

        # 返回是否启动独立的连接管理线程来执行连接处理和OnConnect回调处理
        # OesAsyncApi_IsAsyncConnectAble

        # 设置 Onload 加速标志
        # OesAsyncApi_SetOnloadFlag

        # 返回 Onload 加速标志
        # OesAsyncApi_GetOnloadFlag

        # 设置异步回调线程的忙等待模式
        # OesAsyncApi_SetAsyncCallbackBusyPollAble

        # 返回异步回调线程的忙等待模式
        # OesAsyncApi_IsAsyncCallbackBusyPollAble

        # 返回异步通信队列的长度 (可缓存的最大消息数量)
        self.c_oes_async_api_get_async_queue_length = self.c_api_dll.OesAsyncApi_GetAsyncQueueLength
        self.c_oes_async_api_get_async_queue_length.restype = c_int64
        self.c_oes_async_api_get_async_queue_length.argtypes = [POINTER(OesAsyncApiContextT)]

        # 返回异步通信队列的数据空间大小
        self.c_oes_async_api_get_async_queue_data_area_size = self.c_api_dll.OesAsyncApi_GetAsyncQueueDataAreaSize
        self.c_oes_async_api_get_async_queue_data_area_size.restype = c_int64
        self.c_oes_async_api_get_async_queue_data_area_size.argtypes = [POINTER(OesAsyncApiContextT)]

        # 设置是否启用内置的查询通道
        self.c_oes_async_api_set_builtin_query_able = self.c_api_dll.OesAsyncApi_SetBuiltinQueryable
        self.c_oes_async_api_set_builtin_query_able.restype = c_int
        self.c_oes_async_api_set_builtin_query_able.argtypes = [
            POINTER(OesAsyncApiContextT), c_int
        ]

        # 返回是否启用内置的查询通道
        self.c_oes_async_api_is_builtin_query_able = self.c_api_dll.OesAsyncApi_IsBuiltinQueryable
        self.c_oes_async_api_is_builtin_query_able.restype = c_int
        self.c_oes_async_api_is_builtin_query_able.argtypes = [POINTER(OesAsyncApiContextT)]

        # 返回内置的查询通道是否已连接就绪
        self.c_oes_async_api_is_builtin_query_channel_connected = self.c_api_dll.OesAsyncApi_IsBuiltinQueryChannelConnected
        self.c_oes_async_api_is_builtin_query_channel_connected.restype = c_int
        self.c_oes_async_api_is_builtin_query_channel_connected.argtypes = [POINTER(OesAsyncApiChannelT)]

        # 设置内置的查询通道的配置信息
        # OesAsyncApi_SetBuiltinQueryChannelCfg

        # 从配置文件中加载内置的查询通道的配置信息
        # OesAsyncApi_LoadBuiltinQueryChannelCfg

        # 返回内置的查询通道的配置信息
        # OesAsyncApi_GetBuiltinQueryChannelCfg

        # 返回内置的查询通道的会话信息
        # OesAsyncApi_GetBuiltinQueryChannelRef

        # 设置异步I/O线程配置
        # OesAsyncApi_SetIoThreadCfg

        # 从配置文件中加载异步I/O线程配置
        # OesAsyncApi_LoadIoThreadCfg

        # 返回异步I/O线程配置
        # OesAsyncApi_GetIoThreadCfg

        # 设置异步I/O线程的使能标志
        # OesAsyncApi_SetIoThreadEnabled

        # 返回异步I/O线程的使能标志
        # OesAsyncApi_IsIoThreadEnabled

        # 设置通信线程的线程初始化回调函数
        # OesAsyncApi_SetOnCommunicationThreadStart

        # 设置回调线程的线程初始化回调函数 (如果已启用了独立的回调线程的话)
        # OesAsyncApi_SetOnCallbackThreadStart

        # 设置异步I/O线程的线程初始化回调函数 (如果已启用了异步I/O线程的话)
        # OesAsyncApi_SetOnIoThreadStart
        # -------------------------


        # ===================================================================
        # OES异步API接口函数封装 (查询接口)
        # ===================================================================

        # 获取API的发行版本号
        self.c_oes_async_api_get_api_version = self.c_api_dll.OesAsyncApi_GetApiVersion
        self.c_oes_async_api_get_api_version.restype = c_char_p

        # 获取当前交易日
        self.c_oes_async_api_get_trading_day = self.c_api_dll.OesAsyncApi_GetTradingDay
        self.c_oes_async_api_get_trading_day.restype = c_int32
        self.c_oes_async_api_get_trading_day.argtypes = [POINTER(OesAsyncApiChannelT)]

        # 获取客户端总览信息
        self.c_oes_async_api_get_client_overview = self.c_api_dll.OesAsyncApi_GetClientOverview
        self.c_oes_async_api_get_client_overview.restype = c_int32
        self.c_oes_async_api_get_client_overview.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesClientOverviewT)
        ]

        # 查询客户信息
        self.c_oes_async_api_query_cust_info = self.c_api_dll.OesAsyncApi_QueryCustInfo
        self.c_oes_async_api_query_cust_info.restype = c_int32
        self.c_oes_async_api_query_cust_info.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryCustFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询证券账户信息
        self.c_oes_async_api_query_inv_acct = self.c_api_dll.OesAsyncApi_QueryInvAcct
        self.c_oes_async_api_query_inv_acct.restype = c_int32
        self.c_oes_async_api_query_inv_acct.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryInvAcctFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询现货产品信息
        self.c_oes_async_api_query_stock = self.c_api_dll.OesAsyncApi_QueryStock
        self.c_oes_async_api_query_stock.restype = c_int32
        self.c_oes_async_api_query_stock.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryStockFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询证券发行产品信息
        self.c_oes_async_api_query_issue = self.c_api_dll.OesAsyncApi_QueryIssue
        self.c_oes_async_api_query_issue.restype = c_int32
        self.c_oes_async_api_query_issue.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryIssueFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询ETF申赎产品信息
        self.c_oes_async_api_query_etf = self.c_api_dll.OesAsyncApi_QueryEtf
        self.c_oes_async_api_query_etf.restype = c_int32
        self.c_oes_async_api_query_etf.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryEtfFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询ETF申赎产品信息
        self.c_oes_async_api_query_etf_component = self.c_api_dll.OesAsyncApi_QueryEtfComponent
        self.c_oes_async_api_query_etf_component.restype = c_int32
        self.c_oes_async_api_query_etf_component.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryEtfComponentFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询客户资金信息
        self.c_oes_async_api_query_cash_asset = self.c_api_dll.OesAsyncApi_QueryCashAsset
        self.c_oes_async_api_query_cash_asset.restype = c_int32
        self.c_oes_async_api_query_cash_asset.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryCashAssetFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询两地交易时对端结点的资金资产信息
        self.c_oes_async_api_get_colocation_peer_cash_asset = self.c_api_dll.OesAsyncApi_QueryColocationPeerCashAsset
        self.c_oes_async_api_get_colocation_peer_cash_asset.restype = c_int32
        self.c_oes_async_api_get_colocation_peer_cash_asset.argtypes = [
            POINTER(OesAsyncApiChannelT),
            CCharP,
            POINTER(OesCashAssetItemT)
        ]

        # 查询主柜资金信息
        self.c_oes_async_api_get_counter_cash = self.c_api_dll.OesAsyncApi_QueryCounterCash
        self.c_oes_async_api_get_counter_cash.restype = c_int32
        self.c_oes_async_api_get_counter_cash.argtypes = [
            POINTER(OesAsyncApiChannelT),
            CCharP,
            POINTER(OesCounterCashItemT)
        ]

        # 查询股票持仓信息
        self.c_oes_async_api_query_stk_holding = self.c_api_dll.OesAsyncApi_QueryStkHolding
        self.c_oes_async_api_query_stk_holding.restype = c_int32
        self.c_oes_async_api_query_stk_holding.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryStkHoldingFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询新股配号、中签信息
        self.c_oes_async_api_query_lot_winning = self.c_api_dll.OesAsyncApi_QueryLotWinning
        self.c_oes_async_api_query_lot_winning.restype = c_int32
        self.c_oes_async_api_query_lot_winning.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryLotWinningFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询所有委托信息
        self.c_oes_async_api_query_order = self.c_api_dll.OesAsyncApi_QueryOrder
        self.c_oes_async_api_query_order.restype = c_int32
        self.c_oes_async_api_query_order.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryOrdFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询成交信息
        self.c_oes_async_api_query_trade = self.c_api_dll.OesAsyncApi_QueryTrade
        self.c_oes_async_api_query_trade.restype = c_int32
        self.c_oes_async_api_query_trade.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryTrdFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询出入金流水
        self.c_oes_async_api_query_fund_transfer_serial = self.c_api_dll.OesAsyncApi_QueryFundTransferSerial
        self.c_oes_async_api_query_fund_transfer_serial.restype = c_int32
        self.c_oes_async_api_query_fund_transfer_serial.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryFundTransferSerialFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询佣金信息
        self.c_oes_async_api_query_commission_rate = self.c_api_dll.OesAsyncApi_QueryCommissionRate
        self.c_oes_async_api_query_commission_rate.restype = c_int32
        self.c_oes_async_api_query_commission_rate.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryCommissionRateFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询市场状态信息
        self.c_oes_async_api_query_market_state = self.c_api_dll.OesAsyncApi_QueryMarketState
        self.c_oes_async_api_query_market_state.restype = c_int32
        self.c_oes_async_api_query_market_state.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryMarketStateFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询通知消息
        self.c_oes_async_api_query_notify_info = self.c_api_dll.OesAsyncApi_QueryNotifyInfo
        self.c_oes_async_api_query_notify_info.restype = c_int32
        self.c_oes_async_api_query_notify_info.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryNotifyInfoFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询券商参数信息
        self.c_oes_async_api_query_broker_params_info = self.c_api_dll.OesAsyncApi_QueryBrokerParamsInfo
        self.c_oes_async_api_query_broker_params_info.restype = c_int32
        self.c_oes_async_api_query_broker_params_info.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesBrokerParamsInfoT)
        ]
        # -------------------------


        # ===================================================================
        # OES异步API接口函数封装 (期权业务特有的查询接口)
        # ===================================================================

        # 查询期权产品信息
        self.c_oes_async_api_query_option = self.c_api_dll.OesAsyncApi_QueryOption
        self.c_oes_async_api_query_option.restype = c_int32
        self.c_oes_async_api_query_option.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryOptionFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询期权持仓信息
        self.c_oes_async_api_query_opt_holding = self.c_api_dll.OesAsyncApi_QueryOptHolding
        self.c_oes_async_api_query_opt_holding.restype = c_int32
        self.c_oes_async_api_query_opt_holding.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryOptHoldingFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询期权标的持仓信息
        self.c_oes_async_api_query_opt_underlying_holding = self.c_api_dll.OesAsyncApi_QueryOptUnderlyingHolding
        self.c_oes_async_api_query_opt_underlying_holding.restype = c_int32
        self.c_oes_async_api_query_opt_underlying_holding.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryOptUnderlyingHoldingFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询期权限仓额度信息
        self.c_oes_async_api_query_opt_position_limit = self.c_api_dll.OesAsyncApi_QueryOptPositionLimit
        self.c_oes_async_api_query_opt_position_limit.restype = c_int32
        self.c_oes_async_api_query_opt_position_limit.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryOptPositionLimitFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询期权限购额度信息
        self.c_oes_async_api_query_opt_purchase_limit = self.c_api_dll.OesAsyncApi_QueryOptPurchaseLimit
        self.c_oes_async_api_query_opt_purchase_limit.restype = c_int32
        self.c_oes_async_api_query_opt_purchase_limit.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryOptPurchaseLimitFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询期权行权指派信息
        self.c_oes_async_api_query_opt_exercise_assign = self.c_api_dll.OesAsyncApi_QueryOptExerciseAssign
        self.c_oes_async_api_query_opt_exercise_assign.restype = c_int32
        self.c_oes_async_api_query_opt_exercise_assign.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryOptExerciseAssignFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询期权结算单信息
        self.c_oes_async_api_query_opt_settlement_statement = self.c_api_dll.OesAsyncApi_QueryOptSettlementStatement
        self.c_oes_async_api_query_opt_settlement_statement.restype = c_int64
        self.c_oes_async_api_query_opt_settlement_statement.argtypes = [
            POINTER(OesAsyncApiChannelT),
            CCharP, CCharP, c_int32
        ]
        # -------------------------


        # ===================================================================
        # OES异步API接口函数封装 (融资融券业务特有的查询接口)
        # ===================================================================

        # 查询信用资产信息
        self.c_oes_async_api_query_crd_credit_asset = self.c_api_dll.OesAsyncApi_QueryCrdCreditAsset
        self.c_oes_async_api_query_crd_credit_asset.restype = c_int32
        self.c_oes_async_api_query_crd_credit_asset.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryCrdCreditAssetFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询客户的融资融券可充抵保证金证券及融资融券标的信息
        self.c_oes_async_api_query_crd_underlying_info = self.c_api_dll.OesAsyncApi_QueryCrdUnderlyingInfo
        self.c_oes_async_api_query_crd_underlying_info.restype = c_int32
        self.c_oes_async_api_query_crd_underlying_info.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryCrdUnderlyingInfoFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询融资融券资金头寸信息
        self.c_oes_async_api_query_crd_cash_position = self.c_api_dll.OesAsyncApi_QueryCrdCashPosition
        self.c_oes_async_api_query_crd_cash_position.restype = c_int32
        self.c_oes_async_api_query_crd_cash_position.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryCrdCashPositionFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询融资融券证券头寸信息
        self.c_oes_async_api_query_crd_security_position = self.c_api_dll.OesAsyncApi_QueryCrdSecurityPosition
        self.c_oes_async_api_query_crd_security_position.restype = c_int32
        self.c_oes_async_api_query_crd_security_position.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryCrdSecurityPositionFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询信用持仓信息
        self.c_oes_async_api_query_crd_holding = self.c_api_dll.OesAsyncApi_QueryCrdHolding
        self.c_oes_async_api_query_crd_holding.restype = c_int32
        self.c_oes_async_api_query_crd_holding.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryStkHoldingFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询融资融券合约信息
        self.c_oes_async_api_query_crd_debt_contract = self.c_api_dll.OesAsyncApi_QueryCrdDebtContract
        self.c_oes_async_api_query_crd_debt_contract.restype = c_int32
        self.c_oes_async_api_query_crd_debt_contract.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryCrdDebtContractFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询融资融券合约流水信息
        self.c_oes_async_api_query_crd_debt_journal = self.c_api_dll.OesAsyncApi_QueryCrdDebtJournal
        self.c_oes_async_api_query_crd_debt_journal.restype = c_int32
        self.c_oes_async_api_query_crd_debt_journal.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryCrdDebtJournalFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询融资融券直接还款委托信息
        self.c_oes_async_api_query_crd_cash_repay_order = self.c_api_dll.OesAsyncApi_QueryCrdCashRepayOrder
        self.c_oes_async_api_query_crd_cash_repay_order.restype = c_int32
        self.c_oes_async_api_query_crd_cash_repay_order.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryCrdCashRepayFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询融资融券客户单证券负债统计信息
        self.c_oes_async_api_query_crd_security_debt_stats = self.c_api_dll.OesAsyncApi_QueryCrdSecurityDebtStats
        self.c_oes_async_api_query_crd_security_debt_stats.restype = c_int32
        self.c_oes_async_api_query_crd_security_debt_stats.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryCrdSecurityDebtStatsFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询融资融券余券信息
        self.c_oes_async_api_query_crd_excess_stock = self.c_api_dll.OesAsyncApi_QueryCrdExcessStock
        self.c_oes_async_api_query_crd_excess_stock.restype = c_int32
        self.c_oes_async_api_query_crd_excess_stock.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryCrdExcessStockFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询融资融券息费利率
        self.c_oes_async_api_query_crd_interest_rate = self.c_api_dll.OesAsyncApi_QueryCrdInterestRate
        self.c_oes_async_api_query_crd_interest_rate.restype = c_int32
        self.c_oes_async_api_query_crd_interest_rate.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesQryCrdInterestRateFilterT),
            F_OESAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 查询融资融券业务最大可取资金
        self.c_oes_async_api_get_crd_drawable_balance = self.c_api_dll.OesAsyncApi_GetCrdDrawableBalance
        self.c_oes_async_api_get_crd_drawable_balance.restype = c_int64
        self.c_oes_async_api_get_crd_drawable_balance.argtypes = [
            POINTER(OesAsyncApiChannelT),
            POINTER(OesCrdDrawableBalanceItemT)
        ]

        # 查询融资融券担保品可转出的最大数量
        self.c_oes_async_api_get_crd_collateral_transfer_out_max_qty = self.c_api_dll.OesAsyncApi_GetCrdCollateralTransferOutMaxQty
        self.c_oes_async_api_get_crd_collateral_transfer_out_max_qty.restype = c_int64
        self.c_oes_async_api_get_crd_collateral_transfer_out_max_qty.argtypes = [
            POINTER(OesAsyncApiChannelT),
            CCharP, c_uint8,
            POINTER(OesCrdCollateralTransferOutMaxQtyItemT)
        ]
        # -------------------------


        # ===================================================================
        # OES同步API接口函数封装
        # ===================================================================

        # 初始化日志记录器
        self.c_oes_api_init_logger = self.c_api_dll.OesApi_InitLogger
        self.c_oes_api_init_logger.restype = c_int
        self.c_oes_api_init_logger.argtypes = [CCharP, CCharP]

        # 直接通过指定的参数初始化日志记录器
        self.c_oes_api_init_logger_direct = self.c_api_dll.OesApi_InitLoggerDirect
        self.c_oes_api_init_logger_direct.restype = c_int
        self.c_oes_api_init_logger_direct.argtypes = [
            CCharP, CCharP, CCharP, c_int32, c_int32
        ]

        # 从配置文件中解析远程主机配置
        self.c_oes_api_parse_config_from_file = self.c_api_dll.OesApi_ParseConfigFromFile
        self.c_oes_api_parse_config_from_file.restype = c_int
        self.c_oes_api_parse_config_from_file.argtypes = [
            CCharP, CCharP, CCharP,
            POINTER(OesApiRemoteCfgT),
            POINTER(OesApiSubscribeInfoT)
        ]

        # 解析服务器地址列表字符串
        self.c_oes_api_parse_addr_list_string = self.c_api_dll.OesApi_ParseAddrListString
        self.c_oes_api_parse_addr_list_string.restype = c_int32
        self.c_oes_api_parse_addr_list_string.argtypes = [
            CCharP, POINTER(OesApiAddrInfoT), c_int32
        ]

        # 设置客户端自定义的本地IP和MAC (暂未对外)
        self.c_oes_api_set_customized_ip_and_mac = self.c_api_dll.OesApi_SetCustomizedIpAndMac
        self.c_oes_api_set_customized_ip_and_mac.restype = c_int
        self.c_oes_api_set_customized_ip_and_mac.argtypes = [CCharP, CCharP]

        # 设置客户端自定义的本地IP地址
        self.c_oes_api_set_customized_ip = self.c_api_dll.OesApi_SetCustomizedIp
        self.c_oes_api_set_customized_ip.restype = c_int
        self.c_oes_api_set_customized_ip.argtypes = [CCharP]

        # 获取客户端自定义的本地IP
        self.c_oes_api_get_customized_ip = self.c_api_dll.OesApi_GetCustomizedIp
        self.c_oes_api_get_customized_ip.restype = c_char_p

        # 设置客户端自定义的本地MAC地址
        self.c_oes_api_set_customized_mac = self.c_api_dll.OesApi_SetCustomizedMac
        self.c_oes_api_set_customized_mac.restype = c_int
        self.c_oes_api_set_customized_mac.argtypes = [CCharP]

        # 获取客户端自定义的本地MAC
        self.c_oes_api_get_customized_mac = self.c_api_dll.OesApi_GetCustomizedMac
        self.c_oes_api_get_customized_mac.restype = c_char_p

        # 设置客户端自定义的本地设备序列号
        self.c_oes_api_set_customized_driver_id = self.c_api_dll.OesApi_SetCustomizedDriverId
        self.c_oes_api_set_customized_driver_id.restype = c_int
        self.c_oes_api_set_customized_driver_id.argtypes = [CCharP]

        # 获取客户端自定义的本地设备序列号
        self.c_oes_api_get_customized_driver_id = self.c_api_dll.OesApi_GetCustomizedDriverId
        self.c_oes_api_get_customized_driver_id.restype = c_char_p

        # 设置客户端的交易终端软件名称 (选采项)
        self.c_oes_api_set_client_appl_name = self.c_api_dll.OesApi_SetClientApplName
        self.c_oes_api_set_client_appl_name.restype = c_int
        self.c_oes_api_set_client_appl_name.argtypes = [CCharP]

        # 获取客户端的交易终端软件名称 (选采项)
        self.c_oes_api_get_client_appl_name = self.c_api_dll.OesApi_GetClientApplName
        self.c_oes_api_get_client_appl_name.restype = c_char_p

        # 设置客户端的交易终端软件版本 (选采项)
        self.c_oes_api_set_client_appl_version = self.c_api_dll.OesApi_SetClientApplVerId
        self.c_oes_api_set_client_appl_version.restype = c_int
        self.c_oes_api_set_client_appl_version.argtypes = [CCharP]

        # 获取客户端的交易终端软件版本 (选采项)
        self.c_oes_api_get_client_appl_version = self.c_api_dll.OesApi_GetClientApplVerId
        self.c_oes_api_get_client_appl_version.restype = c_char_p

        # 设置客户端的交易终端设备序列号 (macOS系统为必采项)
        self.c_oes_api_set_device_serial_no = self.c_api_dll.OesApi_SetDeviceSerialNo
        self.c_oes_api_set_device_serial_no.restype = c_int
        self.c_oes_api_set_device_serial_no.argtypes = [CCharP]

        # 获取客户端的交易终端设备序列号 (macOS系统为必采项)
        self.c_oes_api_get_device_serial_no = self.c_api_dll.OesApi_GetDeviceSerialNo
        self.c_oes_api_get_device_serial_no.restype = c_char_p

        # 设置客户端默认的委托方式 (对当前进程生效)
        self.c_oes_api_set_entrust_way = self.c_api_dll.OesApi_SetDefaultEntrustWay
        self.c_oes_api_set_entrust_way.restype = c_int
        self.c_oes_api_set_entrust_way.argtypes = [c_char]

        # 获取客户端默认的委托方式 (对当前进程生效)
        self.c_oes_api_get_entrust_way = self.c_api_dll.OesApi_GetDefaultEntrustWay
        self.c_oes_api_get_entrust_way.restype = c_char

        # 返回通道对应的业务类型
        self.c_oes_api_get_business_type = self.c_api_dll.OesApi_GetBusinessType
        self.c_oes_api_get_business_type.restype = c_uint32
        self.c_oes_api_get_business_type.argtypes = [c_void_p]

        # 返回当前线程最近一次API调用失败的错误号
        self.c_oes_api_get_last_error = self.c_api_dll.OesApi_GetLastError
        self.c_oes_api_get_last_error.restype = c_int32
        self.c_oes_api_get_last_error.argtypes = []

        # 设置当前线程的API错误号
        self.c_oes_api_set_last_error = self.c_api_dll.OesApi_SetLastError
        self.c_oes_api_set_last_error.restype = None
        self.c_oes_api_set_last_error.argtypes = [c_int32]

        # 返回错误号对应的错误信息
        self.c_oes_api_get_error_msg = self.c_api_dll.OesApi_GetErrorMsg
        self.c_oes_api_get_error_msg.restype = c_char_p
        self.c_oes_api_get_error_msg.argtypes = [c_int32]
        # -------------------------


# ===================================================================
# 交易日志接口函数定义
# ===================================================================

c_oes_api_loader = CApiFuncLoader()

log_error = c_oes_api_loader.error
log_info  = c_oes_api_loader.info
log_debug = c_oes_api_loader.debug
log_trace = c_oes_api_loader.trace
# -------------------------
