from pipython import GCSDevice, pitools
from pypylon import pylon
import os
import lib.cmr as cmr
import lib.circle_detection as cdt
import lib.mtr as mtr
import lib.fcs as fcs
import lib.cnf as cnf

# Konfigürasyon dosyasını yükle
cnf.load_config('../config.json')


def main():
    pidevice = mtr.connect_pi(CONTROLLERNAME, SERIALNUM, STAGES, REFMODES)
    camera = cmr.connect_camera(500, EXPOSURE)
    
    # dir değişkenini doğru şekilde atadığından emin ol
    output_dir = DIR  # config.json'dan gelen DIR değişkeni

    # Klasörü oluştur
    os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists
    
    org_width = camera.Width.Value
    org_height = camera.Height.Value
    
    for y in range(STEP_NUM[1] + 1):
        for x in range(STEP_NUM[0] + 1) if y % 2 == 0 else range(STEP_NUM[0] + 1)[::-1]:
            pidevice.MOV(AXES["x"], VERTEX["0,0"][0] + x * DX)
            pidevice.MOV(AXES["y"], VERTEX["0,0"][1] + y * DY)
            
            pitools.waitontarget(pidevice, axes=(AXES["x"], AXES["y"]))

            org_image = cmr.capture_single_image(camera)                

            circles = cdt.get_circle_fft(org_image)
            os.makedirs(os.path.join(output_dir, f"frame{x}_{y}"), exist_ok=True)  # Fixed path

            for idx, circle in enumerate(circles):
                x_c, y_c, r_c = circle

                camera.Width.Value = KERNEL_SIZE[0]
                camera.Height.Value = KERNEL_SIZE[1]
                camera.OffsetX.Value = max(0, x_c - KERNEL_SIZE[0] // 2)  # Fixed offset
                camera.OffsetY.Value = max(0, y_c - KERNEL_SIZE[1] // 2)

                fcs.move_to_focus(pidevice, camera)
                
                camera.StartGrabbingMax(10)

                while camera.IsGrabbing():
                    with camera.RetrieveResult(2000) as result:
                        if result.GrabSucceeded():
                            img = pylon.PylonImage()
                            img.AttachGrabResultBuffer(result)

                            filename = os.path.join(output_dir, f"frame{x}_{y}", f"image{idx}.tiff")
                            img.Save(pylon.ImageFileFormat_Tiff, filename)

                            img.Release()  # Free buffer inside 'with' block

                camera.StopGrabbing()
            
            # Kamera ayarlarını sıfırla
            camera.OffsetX.Value = 0
            camera.OffsetY.Value = 0
            camera.Width.Value = org_width
            camera.Height.Value = org_height


    pidevice.CloseConnection()
    camera.Close()


if __name__ == "__main__":
    main()
