import glob
import os
import numpy as np
import matplotlib.pyplot as plt
from DirectSFG_Processing_methods import Datafiles, ProcessData
import time


def main(
        w1_wavelength: float = 793.27,
        export: bool = False,
        directory: str = "example data/",
        x_lim: tuple[float, float] = (2800, 3800),
        y_lim: tuple[float, float] = (-0.02, 0.1),
        manual_cleaning: list[dict] = None,
) -> None:
    """
    Main function that process our files. Indicate the main parameters here, additional parameters can be adjusted within this function.
    :param w1_wavelength: Visible laser wavelength
    :param export: Set to True to export the processed data (you can change the export directory below)
    :param directory: directory to your data files
    :param x_lim: minimum and maximum wavenumber of interest
    :param y_lim: minimum and maximum intensity of interest
    :param manual_cleaning: Cosmic rays to be manually removed. Enter each peak as a dictionary containing the filename, frame, and the range (in nm) to be removed.
    """
    start_time = time.time()
    print("Let's start processing our SFG data ε> \n")

    # Indicating to manually clean some cosmic rays
    manual_cleaning = [
        {'filename': 'water_ssp_600s_01.csv', 'range': (624.4, 625), 'frame': 2},
        {'filename': 'water_ssp_600s_01.csv', 'range': (635, 636), 'frame': 2},
    ]

    # Grabbing the data files
    glob_list = glob.glob(os.path.join(directory, "*.csv"))
    list_files = [os.path.basename(file) for file in glob_list]
    print(list_files)
    globbing_time = time.time()

    # Organizing data files
    print('\n ---Organizing data files---')
    files = Datafiles(directory, list_files, ref='zqz')
    initdata_time = time.time()
    files.match_signal_to_bg()
    matchbg_time = time.time()
    files.match_sample_to_ref()
    matchref_time = time.time()
    # print(files.dict_datafiles)

    # Processing the data
    print('\n ---Processing the data---')
    dat = ProcessData(files.dict_datafiles)
    initprocess_time = time.time()
    dat.remove_cosmic_rays(automatic=True, manual=manual_cleaning)
    cosmicray_time = time.time()
    dat.average_frames()
    average_time = time.time()
    dat.subtract_bg()
    subtractbg_time = time.time()
    dat.normalize(w1_wavelength)
    normalize_time = time.time()

    # if true, saves the processed data
    if export:
        dat.save_processed_data(directory='processed_data', script_name=os.path.basename(__file__), w1=w1_wavelength)

    print('\n --- Plotting ---')
    # Plotting raw data
    print('Plotting raw data')
    fig1, ax1 = plt.subplots(nrows=2, ncols=3, figsize=(15, 8), dpi=100)

    for datafile in dat.datafiles.get('ref'):
        ax1[0, 0].plot(datafile.get('data')['Wavelength'], datafile.get('data')['Intensity'],
                       label=datafile.get('filename'), alpha=0.7, linewidth=0.75)
        if 'cleaned points' in datafile:
            ax1[0, 0].scatter(datafile.get('cleaned points')[:, 0], datafile.get('cleaned points')[:, 1],
                              marker='x', color='red')
    for datafile in dat.datafiles.get('sample'):
        ax1[0, 1].plot(datafile.get('data')['Wavelength'], datafile.get('data')['Intensity'],
                       label=datafile.get('filename'), alpha=0.7, linewidth=0.75)
        if 'cleaned points' in datafile:
            ax1[0, 1].scatter(datafile.get('cleaned points')[:, 0], datafile.get('cleaned points')[:, 1],
                              marker='x', color='red')
    for datafile in dat.datafiles.get('calibration'):
        ax1[0, 2].plot(datafile.get('data')['Wavelength'], datafile.get('data')['Intensity'],
                       label=datafile.get('filename'), alpha=0.7, linewidth=0.75)
        if 'cleaned points' in datafile:
            ax1[0, 2].scatter(datafile.get('cleaned points')[:, 0], datafile.get('cleaned points')[:, 1],
                              marker='x', color='red')
    for datafile in dat.datafiles.get('bg'):
        ax1[1, 0].plot(datafile.get('data')['Wavelength'], datafile.get('data')['Intensity'],
                       label=datafile.get('filename'), alpha=0.7, linewidth=0.75)
        if 'cleaned points' in datafile:
            ax1[1, 0].scatter(datafile.get('cleaned points')[:, 0], datafile.get('cleaned points')[:, 1],
                              marker='x', color='red')
    # for datafile in dat.datafiles.get('sample'):
    #     ax1[1,1].plot(datafile.get('data')['Wavelength'], datafile.get('data')['Intensity'],
    #                        label=datafile.get('filename'), alpha=0.7, linewidth=0.75)
    #     if 'cleaned points' in  datafile:
    #         ax1[1,1].scatter(datafile.get('cleaned points')[:, 0], datafile.get('cleaned points')[:, 1],
    #             marker='x', color='red')
    for datafile in dat.datafiles.get('calibration'):
        ax1[1, 2].plot(datafile.get('data processed')['Wavenumber'], datafile.get('data processed')['Intensity'],
                       label=datafile.get('filename'), alpha=0.7, linewidth=0.75)

    ax1[0, 0].set_title('Ref raw data')
    ax1[0, 1].set_title('Sample raw data')
    ax1[0, 2].set_title('Calibration')
    ax1[1, 0].set_title('Background data')
    # ax1[1,1].set_title('sample bkg data')
    ax1[1, 2].set_title('Processed calibration')
    for ax in ax1.flat:
        ax.legend(fontsize=8)

    plotraw_time = time.time()

    # Plotting processed data
    print('Plotting processed data')
    fig2, ax_2 = plt.subplots(figsize=(12, 8))
    ax_2.set_title('Processed samples')
    ax_2.set_prop_cycle('color', [plt.cm.plasma(i) for i in np.linspace(0, 0.8, len(dat.datafiles.get('sample')))])
    ax_2.set_xlabel(r"Frequency (cm$^{-1}$)")
    ax_2.set_ylabel("Intensity (a.u.)")
    for sample in dat.datafiles.get('sample'):
        label = sample.get('sample') + ' ' + sample.get('polarization') + ' ' + sample.get('index')
        ax_2.plot(sample.get('data processed')['Wavenumber'], sample.get('data processed')['Intensity'],
                  label=label, alpha=0.6)
        ax_2.set_xlim(x_lim)
        ax_2.set_ylim(y_lim)
        ax_2.legend(fontsize=10)
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(sample.get('data processed')['Wavenumber'], sample.get('data processed')['Intensity'],
                color="0.2")
        ax.set_xlim(x_lim)
        ax.set_ylim(y_lim)
        ax.set_xlabel(r"Frequency (cm$^{-1}$)")
        ax.set_ylabel("Intensity (a.u.)")
        ax.set_title(label)
        fig.tight_layout()

    print('Processed finished! xoxo ε>')
    finish_time = time.time()

    # print the script performance
    print('\n Time elapsed \n',
          "init + globbing: %.1f ms \n" % ((globbing_time - start_time) * 1000),
          "init datafiles: %.1f ms \n" % ((initdata_time - globbing_time) * 1000),
          "match bg: %.1f ms \n" % ((matchbg_time - initdata_time) * 1000),
          "match ref: %.1f ms \n" % ((matchref_time - matchbg_time) * 1000),
          "init process data: %.1f ms \n" % ((initprocess_time - matchref_time) * 1000),
          "remove cosmic rays: %.1f ms \n" % ((cosmicray_time - initprocess_time) * 1000),
          "average frames: %.1f ms \n" % ((average_time - cosmicray_time) * 1000),
          "subtract bg: %.1f ms \n" % ((subtractbg_time - average_time) * 1000),
          "normalize: %.1f ms \n" % ((normalize_time - subtractbg_time) * 1000),
          "plot raw data: %.1f ms \n" % ((plotraw_time - normalize_time) * 1000),
          "plot processed data: %.1f ms \n" % ((finish_time - plotraw_time) * 1000),
          "- all: %.1f ms" % ((finish_time - start_time) * 1000),
          )

    fig1.tight_layout()
    fig2.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
