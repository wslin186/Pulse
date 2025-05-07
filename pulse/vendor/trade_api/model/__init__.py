# -*- coding: utf-8 -*-

try:
    from .spk_util import *
    from .spk_util import (
        SEndpointContextT as OesAsyncApiContextT,
        SEndpointChannelT as OesAsyncApiChannelT,
        SEndpointChannelCfgT as OesAsyncApiChannelCfgT,
        SGeneralClientAddrInfoT as OesApiAddrInfoT,
        SGeneralClientRemoteCfgT as OesApiRemoteCfgT,
    )
except ImportError:
    from sutil.spk_util import *
    from sutil.spk_util import (
        SEndpointContextT as OesAsyncApiContextT,
        SEndpointChannelT as OesAsyncApiChannelT,
        SEndpointChannelCfgT as OesAsyncApiChannelCfgT,
        SGeneralClientAddrInfoT as OesApiAddrInfoT,
        SGeneralClientRemoteCfgT as OesApiRemoteCfgT,
    )

from .oes_base_constants import *

from .oes_base_model_credit import *
from .oes_base_model_credit import (
    OesCrdDebtContractReportT as OesCrdDebtContractItemT,
    OesCrdExcessStockBaseInfoT as OesCrdExcessStockItemT,
    OesCrdDebtJournalBaseInfoT as OesCrdDebtJournalItemT,
    OesCrdUnderlyingBaseInfoT as OesCrdUnderlyingInfoItemT
)

from .oes_base_model_option import *
from .oes_base_model_option import (
    OesOptionBaseInfoT as OesOptionItemT,
    OesOptionExerciseAssignBaseT as OesOptExerciseAssignItemT,
    OesOptUnderlyingHoldingBaseInfoT as OesOptUnderlyingHoldingItemT,
    OesOptSettlementConfirmReportT as OesOptSettlementConfirmRspT
)

from .oes_base_model import *
from .oes_base_model import (
    OesOrdCnfmT as OesOrdItemT,
    OesTrdCnfmT as OesTrdItemT,
    OesCashAssetReportT as OesCashAssetItemT,
    OesFundTrsfReportT as OesFundTransferSerialItemT,
    OesEtfBaseInfoT as OesEtfItemT,
    OesIssueBaseInfoT as OesIssueItemT,
    OesStockBaseInfoT as OesStockItemT,
    OesStkHoldingReportT as OesStkHoldingItemT,
    OesLotWinningBaseInfoT as OesLotWinningItemT,
    OesCrdCreditAssetBaseInfoT as OesCrdCreditAssetItemT,
    OesCrdSecurityDebtStatsBaseInfoT as OesCrdSecurityDebtStatsItemT,
    OesCrdCashRepayReportT as OesCrdCashRepayItemT,

    # @note mgr_client专用
    __OES_ORD_BASE_INFO_PKT,
    __OES_ORD_REQ_LATENCY_FIELDS,
    __OES_ORD_CNFM_BASE_INFO_PKT,
    __OES_ORD_CNFM_LATENCY_FIELDS,
    __OES_ORD_CNFM_EXT_INFO_PKT,
    __OES_TRD_BASE_INFO_PKT,
    __OES_TRD_CNFM_BASE_INFO_PKT,
    __OES_TRD_CNFM_LATENCY_FIELDS,
    __OES_TRD_CNFM_EXT_INFO_PKT,
)

from .oes_qry_packets import *

from .oes_qry_packets_credit import *

from .oes_qry_packets_option import *

from .oes_packets import *
from .oes_packets import (
    OesNotifyInfoReportT as OesNotifyInfoItemT
)
