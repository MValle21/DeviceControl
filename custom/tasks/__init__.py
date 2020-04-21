from custom.tasks import PBR, GAS, TH_IB2, U1W_TVSL

classes = {
    "U1W_TVSL_measure_all": U1W_TVSL.MeasureAll,
    "TH_IB2_measure_all": TH_IB2.MeasureAll,
    "PBR_measure_all": PBR.PBRMeasureAll,
    "PSI_PBR_pump": PBR.PBRGeneralPump,
    "GAS_measure_all": GAS.GASMeasureAll
}
