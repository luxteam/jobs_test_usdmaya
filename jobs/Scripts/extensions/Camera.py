def init_viewport(case):
    mel.eval('modelEditor -e -rom \"FireRenderOverride\" modelPanel4')
    rpr_render(case)

def save_viewport(case):
    for i in range(0, 100):
        cmds.refresh(currentView=True, fe='png', fn=WORK_DIR+'/Color/'+case['case']+'.jpg')

def reset_attributes():
    mel.eval('setAttr "perspShape.horizontalFilmAperture" 1.417')
    mel.eval('setAttr "perspShape.verticalFilmAperture" 0.945')
    mel.eval('setAttr "perspShape.focalLength" 35')
    mel.eval('setAttr "perspShape.cameraScale" 1')
    mel.eval('setAttr "perspShape.lensSqueezeRatio" 1')
    mel.eval('setAttr "perspShape.shakeEnabled" 0')
    mel.eval('setAttr "perspShape.horizontalShake" 0')
    mel.eval('setAttr "perspShape.verticalShake" 0')
    mel.eval('setAttr "perspShape.shakeOverscanEnabled" 0')
    mel.eval('setAttr "perspShape.preScale" 1')
    mel.eval('setAttr "perspShape.filmTranslateH" 0')
    mel.eval('setAttr "perspShape.filmTranslateV" 0')
    mel.eval('setAttr "perspShape.horizontalRollPivot" 0')
    mel.eval('setAttr "perspShape.verticalRollPivot" 0')
    mel.eval('setAttr "perspShape.filmRollValue" 0')
    mel.eval('setAttr "perspShape.postScale" 1')
    mel.eval('setAttr "perspShape.filmRollOrder" 0')