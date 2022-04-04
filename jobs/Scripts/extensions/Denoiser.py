def setup_denoiser(min_iterations=4, denoiser_step=32):
    cmds.setAttr("defaultRenderGlobals.HdRprPlugin_Prod___rpr_mtohns_denoising_mtohns_enable", 1)
    cmds.setAttr("defaultRenderGlobals.HdRprPlugin_Prod___rpr_mtohns_denoising_mtohns_minIter", min_iterations)
    cmds.setAttr("defaultRenderGlobals.HdRprPlugin_Prod___rpr_mtohns_denoising_mtohns_iterStep", denoiser_step)
