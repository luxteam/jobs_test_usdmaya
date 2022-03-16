import os
import maya.cmds as cmds
import maya.mel as mel


def main():
    try:
        if not cmds.pluginInfo("mayaUsdPlugin", query=True, loaded=True):
            print("[INFO] mayaUsdPlugin plugin is not loaded. Loading plugin ...")
            cmds.loadPlugin('mayaUsdPlugin')
    except Exception as err:
        print("[ERROR] Failed to load mayaUsdPlugin plugin. Error message: {}".format(str(err)))
        cmds.quit(abort=True)
        
    try:
        if not cmds.pluginInfo("mtoh", query=True, loaded=True):
            print("[INFO] mtoh plugin is not loaded. Loading mtoh plugin ...")
            cmds.loadPlugin('mtoh')
    except Exception as err:
        print("[ERROR] Failed to load mtoh plugin. Error message: {}".format(str(err)))
        cmds.quit(abort=True)

    print("[INFO] mayaUsdPlugin and mtoh plugins has been successfully loaded.")

    try:
        print("[INFO] Preparing configurations for rendering...")
        cmds.setAttr('defaultRenderGlobals.currentRenderer', 'rprUsdRender', type='string')
        
        engine = os.getenv('ENGINE', 'Northstar')
        if engine == 'Northstar':
            cmds.setAttr('defaultRenderGlobals.HdRprPlugin_Prod___rpr_mtohns_core_mtohns_renderQuality', 5)
        elif engine == 'HybridLow':
            cmds.setAttr("defaultRenderGlobals.HdRprPlugin_Prod___rpr_mtohns_core_mtohns_renderQuality", 0)
        elif engine == 'HybridMedium':
            cmds.setAttr("defaultRenderGlobals.HdRprPlugin_Prod___rpr_mtohns_core_mtohns_renderQuality", 1)
        elif engine == 'HybridHigh':
            cmds.setAttr("defaultRenderGlobals.HdRprPlugin_Prod___rpr_mtohns_core_mtohns_renderQuality", 2)
        elif engine == 'HybridPro':
            cmds.setAttr("defaultRenderGlobals.HdRprPlugin_Prod___rpr_mtohns_core_mtohns_renderQuality", 3)
            
        print("[INFO] Current render engine: {}.".format(engine))
        cmds.setAttr('defaultRenderGlobals.imageFormat', 8)
        
        mel.eval('rprUsdRender -cam persp -h 800 -w 600 -wft')
        mel.eval('renderIntoNewWindow render')
        
        results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Work', 'Results', 'Maya')
        cmds.sysFile(results_dir, makeDir=True)
        test_case_path = os.path.join(results_dir, 'cache_building')
        cmds.renderWindowEditor('renderView', edit=1,  dst='color')
        cmds.renderWindowEditor('renderView', edit=1, com=1, writeImage=test_case_path)
        print("[INFO] Render has been finished")
    except Exception as err:
        print("[ERROR] Failed to render the scene. Error message: {}".format(str(err)))
        cmds.quit(abort=True)
    finally:
        print("[INFO] Closing Maya.")
        cmds.evalDeferred("cmds.quit(abort=True)")


cmds.evalDeferred("cache_building.main()")
