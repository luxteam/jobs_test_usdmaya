import maya.mel as mel
import maya.cmds as cmds
import glob
import datetime
import time
import json
import re
import os.path as path
import os
from event_recorder import event
from shutil import copyfile, move
from collections import deque

WORK_DIR = '{work_dir}'
TEST_TYPE = '{testType}'
RENDER_DEVICE = '{render_device}'
RES_PATH = '{res_path}'
PASS_LIMIT = {pass_limit}
RESOLUTION_X = {resolution_x}
RESOLUTION_Y = {resolution_y}
SPU = {SPU}
THRESHOLD = {threshold}
ENGINE = '{engine}'
RETRIES = {retries}
BATCH_RENDER = {batch_render}
LOGS_DIR = path.join(WORK_DIR, 'render_tool_logs')
RENDER_TOOL_LOG = path.join(WORK_DIR, 'renderTool.log')

def logging(message, case=None):
    message = ' >>> [RPR TEST] [' + datetime.datetime.now().strftime('%H:%M:%S') + '] ' + message
    print(message)
    if BATCH_RENDER and case is not None:
        with open(RENDER_TOOL_LOG, 'a') as f:
            f.write(message + '\n')
    

def reportToJSON(case, render_time=0):
    path_to_file = path.join(WORK_DIR, case['case'] + '_RPR.json')

    with open(path_to_file, 'r') as file:
        report = json.loads(file.read())[0]

    # status for Athena suite will be set later
    if case['status'] == 'inprogress':
        if BATCH_RENDER:
            case['status'] = 'done'
        report['test_status'] = 'passed'
        report['group_timeout_exceeded'] = False
    elif case['status'] == 'inprogress_observed':
        if BATCH_RENDER:
            case['status'] = 'done'
        report['test_status'] = 'observed'
        report['group_timeout_exceeded'] = False

    logging('Create report json ({{}} {{}})'.format(
            case['case'], report['test_status']), case['case'])

    number_of_tries = case.get('number_of_tries', 0)
    if case['status'] == 'error':
        # remove old message
        for message in report['message']:
            if 'Testcase wasn\'t executed successfully' in message:
                report['message'].remove(message)
        if number_of_tries == RETRIES:
            error_message = 'Testcase wasn\'t executed successfully (all attempts were used)'
        else:
            error_message = 'Testcase wasn\'t executed successfully'
        report['message'].append(error_message)
        report['group_timeout_exceeded'] = False
    else:
        report['message'] = []

    report['date_time'] = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    if 'render_start_time' in case:
        report['render_start_time'] = case['render_start_time']
    if 'render_end_time' in case:
        report['render_end_time'] = case['render_end_time']
    report['render_time'] = render_time
    report['test_group'] = TEST_TYPE
    report['test_case'] = case['case']
    report['case_functions'] = case['functions']
    report['difference_color'] = 0
    report['script_info'] = case['script_info']
    report['render_log'] = path.join('render_tool_logs', case['case'] + '.log')
    report['scene_name'] = case.get('scene', '')
    report['number_of_tries'] = number_of_tries
    report['engine'] = ENGINE
    if case['status'] != 'skipped':
        report['file_name'] = case['case'] + case.get('extension', '.jpg')
        report['render_color_path'] = path.join('Color', report['file_name'])

    # save metrics which can be received witout call of functions of Maya
    with open(path_to_file, 'w') as file:
        file.write(json.dumps([report], indent=4))

    try:
        report['tool'] = mel.eval('about -iv')
    except Exception as e:
        logging('Failed to get Maya version. Reason: {{}}'.format(str(e)), case['case'])

    # save metrics which can't be received witout call of functions of Maya (additional measures to avoid stucking of Maya)
    with open(path_to_file, 'w') as file:
        file.write(json.dumps([report], indent=4))


def render_tool_log_path(name):
    return path.join(LOGS_DIR, name + '.log')


def get_scene_path(case):
    scenePath = os.path.join(RES_PATH, 'Scenes')
    temp = os.path.join(scenePath, case['scene'][:-3])
    if os.path.isdir(temp):
        scenePath = temp
    return scenePath


def extract_img_from(folder, case):
    src_dir = path.join(WORK_DIR, 'Color', folder)
    img_name = cmds.renderSettings(firstImageName=True)[0]
        
    if os.path.exists(src_dir) and os.path.isdir(src_dir):
        try:
            move(path.join(src_dir, img_name), path.join(WORK_DIR, 'Color'))
            logging('Extract {{}} from {{}} folder'.format(img_name, folder), case['case'])
        except Exception as ex:
            logging('Error while extracting {{}} from {{}}: {{}}'.format(img_name, folder, ex), case['case'])
    else:
        logging("{{}} doesn't exist or isn't a folder".format(folder), case['case'])


def validateFiles(case):
    logging('Repath scene', case['case'])
    cmds.filePathEditor(refresh=True)
    unresolved_files = cmds.filePathEditor(query=True, listFiles='', unresolved=True, attributeOnly=True)
    source_path = os.path.join(RES_PATH, 'Sources')
    logging("Unresolved items: {{}}".format(str(unresolved_files)), case['case'])
    logging('Start repath scene', case['case'])
    logging("Source (target) path: {{}}".format(source_path), case['case'])
    if unresolved_files:
        for item in unresolved_files:
            cmds.filePathEditor(item, repath=source_path, recursive=True, ra=1)
    unresolved_files = cmds.filePathEditor(query=True, listFiles='', unresolved=True, attributeOnly=True)
    logging("Unresolved items: {{}}".format(str(unresolved_files)), case['case'])
    logging('Repath finished', case['case'])


def apply_case_functions(case, start_index, end_index):
    for function in case['functions'][start_index:end_index]:
        try:
            if re.match('((^\S+|^\S+ \S+) = |^print|^if|^for|^with)', function):
                exec(function)
            else:
                eval(function)
        except Exception as e:
            logging('Error "{{}}" with string "{{}}"'.format(e, function), case['case'])


def enable_rpr(case):
    event('Load plugin', True, case)
    cmds.loadPlugin('mayaUsdPlugin', quiet=True)
    cmds.loadPlugin('mtoh', quiet=True)
    event('Load plugin', False, case)
    logging('Load plugin', case)


def rpr_render(case, mode='color'):
    event('Prerender', False, case['case'])
    validateFiles(case)

    image_path = path.join(WORK_DIR, 'Color', case['case'] + case.get('extension', '.jpg'))

    if path.exists(image_path):
        logging('Remove existing image', case['case'])
        os.remove(image_path)

    logging('Render image', case['case'])

    mel.eval('rprUsdRender -cam persp -h 800 -w 600 -wft')
    render_start_time = datetime.datetime.now()
    case['render_start_time'] = str(render_start_time)
    mel.eval('renderIntoNewWindow render')
    cmds.sysFile(path.join(WORK_DIR, 'Color'), makeDir=True)
    test_case_path = path.join(WORK_DIR, 'Color', case['case'])
    cmds.renderWindowEditor('renderView', edit=1,  dst=mode)
    cmds.renderWindowEditor('renderView', edit=1, com=1,
                            writeImage=test_case_path)
    render_end_time = datetime.datetime.now()
    case['render_end_time'] = str(render_end_time)
    test_time = (render_end_time - render_start_time).total_seconds()
    event('Postrender', True, case['case'])
    reportToJSON(case, test_time)


def postrender(case_num):
    with open(path.join(WORK_DIR, 'test_cases.json'), 'r') as json_file:
        cases = json.load(json_file)
    case = cases[case_num]

    if 'render_start_time' in case:
        render_end_time = datetime.datetime.now()
        case['render_end_time'] = str(render_end_time)
        test_time = (render_end_time - datetime.datetime.strptime(case['render_start_time'], '%Y-%m-%d %H:%M:%S.%f')).total_seconds()
    else:
        test_time = -0.0

    logging('Postrender', case['case'])
    event("Postrender", True, case['case'])
    reportToJSON(case, test_time)

    apply_case_functions(case, case['functions'].index("rpr_render(case)") + 1, len(case['functions']))
    event("Postrender", False, case['case'])

    case_end_time = datetime.datetime.now()
    case['case_end_time'] = str(case_end_time)
    case['time_taken'] = (case_end_time - datetime.datetime.strptime(case['case_start_time'], '%Y-%m-%d %H:%M:%S.%f')).total_seconds()

    with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
        json.dump(cases, file, indent=4)

    event("Close tool", True, case['case'])


def prerender(case):
    logging('Prerender', case['case'])
    if not BATCH_RENDER:
        scene = case.get('scene', '')

        scenePath = os.path.join(get_scene_path(case), scene)
        logging("Scene path: {{}}".format(scenePath))

        scene_name = cmds.file(q=True, sn=True, shn=True)
        if scene_name != scene:
            try:
                event('Open scene', True, case['case'])
                cmds.file(scenePath, f=True, op='v=0;', prompt=False, iv=True, o=True)
                event('Open scene', False, case['case'])
                enable_rpr(case['case'])
            except Exception as e:
                logging(
                    "Can't prepare for render scene because of {{}}".format(str(e)))

        event("Prerender", True, case['case'])
    else:
        enable_rpr(case['case'])
        event("Prerender", True, case['case'])

    if ENGINE == 'Northstar':
        cmds.setAttr('defaultRenderGlobals.HdRprPlugin_Prod___rpr_mtohns_core_mtohns_renderQuality', 5)
    elif ENGINE == 'HybridLow':
        cmds.setAttr("defaultRenderGlobals.HdRprPlugin_Prod___rpr_mtohns_core_mtohns_renderQuality", 0)
    elif ENGINE == 'HybridMedium':
        cmds.setAttr("defaultRenderGlobals.HdRprPlugin_Prod___rpr_mtohns_core_mtohns_renderQuality", 1)
    elif ENGINE == 'HybridHigh':
        cmds.setAttr("defaultRenderGlobals.HdRprPlugin_Prod___rpr_mtohns_core_mtohns_renderQuality", 2)
    elif ENGINE == 'HybridPro':
        cmds.setAttr("defaultRenderGlobals.HdRprPlugin_Prod___rpr_mtohns_core_mtohns_renderQuality", 3)

    if RESOLUTION_X and RESOLUTION_Y:
        cmds.setAttr('defaultResolution.width', RESOLUTION_X)
        cmds.setAttr('defaultResolution.height', RESOLUTION_Y)

    cmds.setAttr('defaultRenderGlobals.currentRenderer', 'rprUsdRender', type='string')
                 
    cmds.setAttr('defaultRenderGlobals.imageFormat', 8)

    cmds.setAttr('defaultRenderGlobals.HdRprPlugin_Prod___rpr_mtohns_adaptiveSampling_mtohns_noiseTreshold', THRESHOLD)
    cmds.setAttr('defaultRenderGlobals.HdRprPlugin_Prod___rpr_mtohns_maxSamples', PASS_LIMIT)

    if not BATCH_RENDER:
        apply_case_functions(case, 0, len(case['functions']))
    else:
        apply_case_functions(case, 0, case['functions'].index("rpr_render(case)") + 1)




def save_report(case):
    logging('Save report without rendering for ' + case['case'])

    if not os.path.exists(os.path.join(WORK_DIR, 'Color')):
        os.makedirs(os.path.join(WORK_DIR, 'Color'))

    work_dir = path.join(WORK_DIR, 'Color', case['case'] + '.jpg')
    source_dir = path.join(WORK_DIR, '..', '..', '..',
                           '..', 'jobs_launcher', 'common', 'img')

    # image for Athena suite will be set later
    if TEST_TYPE not in ['Athena']:
        if case['status'] == 'inprogress' or case['status'] == 'observed':
            copyfile(path.join(source_dir, 'passed.jpg'), work_dir)
        elif case['status'] != 'skipped':
            copyfile(
                path.join(source_dir, case['status'] + '.jpg'), work_dir)

    enable_rpr(case['case'])

    reportToJSON(case)


def case_function(case):
    functions = {{
        'prerender': prerender,
        'save_report': save_report
    }}

    func = 'prerender'

    if case['functions'][0] == 'check_test_cases_success_save':
        func = 'save_report'
    else:
        try:
            logging("SetProject skipped.")
            '''
            projPath = os.path.join(RES_PATH, TEST_TYPE)
            temp = os.path.join(projPath, case['scene'][:-3])
            if os.path.isdir(temp):
                projPath = temp
            mel.eval('setProject("{{}}")'.format(projPath.replace('\\', '/')))
            '''
        except:
            pass
            # logging("Can't set project in '" + projPath + "'")

    if case['status'] == 'fail' or case.get('number_of_tries', 0) >= RETRIES:
        case['status'] = 'error'
        func = 'save_report'
    elif case['status'] == 'skipped':
        func = 'save_report'
    else:
        case['number_of_tries'] = case.get('number_of_tries', 0) + 1

    functions[func](case)


# place for extension functions


def main(case_num=None):
    with open(path.join(WORK_DIR, 'test_cases.json'), 'r') as json_file:
        cases = json.load(json_file)

    event('Open tool', False, next(
        case['case'] for case in cases if case['status'] in ['active', 'observed', 'fail', 'skipped']))
    if not BATCH_RENDER:
        for case in cases:
            if case['status'] in ['active', 'observed', 'fail', 'skipped']:
                if case['status'] == 'active':
                    case['status'] = 'inprogress'
                elif case['status'] == 'observed':
                    case['status'] = 'inprogress_observed'

                with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
                    json.dump(cases, file, indent=4)

                log_path = render_tool_log_path(case['case'])
                if not path.exists(log_path):
                    with open(log_path, 'w'):
                        logging('Create log file for ' + case['case'])
                cmds.scriptEditorInfo(historyFilename=log_path, writeHistory=True)

                logging(case['case'] + ' in progress')

                case_start_time = datetime.datetime.now()
                case['case_start_time'] = str(case_start_time)
                case_function(case)
                case_end_time = datetime.datetime.now()
                case['case_end_time'] = str(case_end_time)
                case['time_taken'] = (case_end_time - case_start_time).total_seconds()

                if case['status'] == 'inprogress' or case['status'] == 'inprogress_observed':
                    case['status'] = 'done'
                    logging(case['case'] + ' done')
                
                with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
                    json.dump(cases, file, indent=4)

        event('Close tool', True, cases[-1]['case'])

        cmds.quit(abort=True)

    else:
        case = cases[case_num]

        if case['status'] == 'active':
            case['status'] = 'inprogress'
        elif case['status'] == 'observed':
            case['status'] = 'inprogress_observed'

        case['case_start_time'] = str(datetime.datetime.now())
        case['number_of_tries'] = case.get('number_of_tries', 0) + 1
        
        with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
            json.dump(cases, file, indent=4)
        prerender(case)
        with open(path.join(WORK_DIR, 'test_cases.json'), 'w') as file:
            json.dump(cases, file, indent=4)
