import json

def load_config(config_file_path):
    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)

    # STEP_NUM hesaplama
    STEP_NUM = [
        int(abs(config['VERTEX']["0,0"][0] - config['VERTEX']["1,1"][0]) // config['DX']),
        int(abs(config['VERTEX']["0,0"][1] - config['VERTEX']["1,1"][1]) // config['DY']),
    ]
    
    # Konfigürasyondan değişkenleri ayıkla ve globalde atama yap
    globals()['CONTROLLERNAME'] = config['CONTROLLERNAME']
    globals()['STAGES'] = config['STAGES']
    globals()['REFMODES'] = config['REFMODES']
    globals()['SERIALNUM'] = config['SERIALNUM']
    globals()['DY'], globals()['DX'] = config['DY'], config['DX']
    globals()['VERTEX'] = {key: tuple(value) for key, value in config['VERTEX'].items()}
    globals()['STEP_NUM'] = STEP_NUM
    globals()['AXES'] = config['AXES']
    globals()['DIR'] = config['DIR']
    globals()['KERNEL_SIZE'] = tuple(config['KERNEL_SIZE'])
    globals()['EXPOSURE'] = config['EXPOSURE']  # Corrected line
