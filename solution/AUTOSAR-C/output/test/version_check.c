#if (CDD_IPC_VENDOR_ID_C != CDD_IPC_VENDOR_ID)
#error "Cdd_Ipc.c and Cdd_Ipc.h have different vendor ids"
#endif

#if (CDD_IPC_MODULE_ID_C != CDD_IPC_MODULE_ID) || \
    (CDD_IPC_AR_RELEASE_MAJOR_VERSION_C != CDD_IPC_AR_RELEASE_MAJOR_VERSION) || \
    (CDD_IPC_AR_RELEASE_MINOR_VERSION_C != CDD_IPC_AR_RELEASE_MINOR_VERSION)
#error "AutoSar Version Numbers of Cdd_Ipc.c and Cdd_Ipc.h are different"
#endif

#if (CDD_IPC_AR_RELEASE_REVISION_VERSION_C != CDD_IPC_AR_RELEASE_REVISION_VERSION) || \
    (CDD_IPC_SW_MAJOR_VERSION_C != CDD_IPC_SW_MAJOR_VERSION) || \
    (CDD_IPC_SW_MINOR_VERSION_C != CDD_IPC_SW_MINOR_VERSION)
#error "Software Version Numbers of Cdd_Ipc.c and Cdd_Ipc.h are different"
#endif

#if (CDD_IPC_VENDOR_ID_C != CDD_IPC_PBCFG_VENDOR_ID)
#error "Cdd_Ipc.c and Cdd_Ipc_PBcfg.h have different vendor ids"
#endif

#if (CDD_IPC_MODULE_ID_C != CDD_IPC_PBCFG_MODULE_ID) || \
    (CDD_IPC_AR_RELEASE_MAJOR_VERSION_C != CDD_IPC_PBCFG_AR_RELEASE_MAJOR_VERSION) || \
    (CDD_IPC_AR_RELEASE_MINOR_VERSION_C != CDD_IPC_PBCFG_AR_RELEASE_MINOR_VERSION)
#error "AutoSar Version Numbers of Cdd_Ipc.c and Cdd_Ipc_PBcfg.h are different"
#endif

#if (CDD_IPC_AR_RELEASE_REVISION_VERSION_C != CDD_IPC_PBCFG_AR_RELEASE_REVISION_VERSION) || \
    (CDD_IPC_SW_MAJOR_VERSION_C != CDD_IPC_PBCFG_SW_MAJOR_VERSION) || \
    (CDD_IPC_SW_MINOR_VERSION_C != CDD_IPC_PBCFG_SW_MINOR_VERSION)
#error "Software Version Numbers of Cdd_Ipc.c and Cdd_Ipc_PBcfg.h are different"
#endif

