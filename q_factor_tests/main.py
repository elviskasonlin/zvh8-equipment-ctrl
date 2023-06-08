import operator

import scipy as sp
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from typing import Iterable, Tuple
import timeit

pow = [-8.893078804, -8.868774414, -8.938971519, -9.018967628, -9.108658791, -9.207920074, -9.278100014, -9.387408257,
       -9.435790062, -9.503517151, -9.566358566, -9.608409882, -9.690438271, -9.75394249, -9.834890366, -9.937273026,
       -10.0908165, -10.23912811, -10.34248161, -10.40677166, -10.38444328, -10.37195206, -10.28402233, -10.20179176,
       -10.09536743, -9.929371834, -9.759595871, -9.611453056, -9.437253952, -9.3210783, -9.178812027, -9.097649574,
       -8.982862473, -8.941099167, -8.871048927, -8.764665604, -8.65897274, -8.601483345, -8.541783333, -8.497846603,
       -8.435375214, -8.381410599, -8.320670128, -8.245782852, -8.21062851, -8.181755066, -8.187655449, -8.201496124,
       -8.253734589, -8.272414207, -8.327569008, -8.3080616, -8.278162956, -8.258570671, -8.187056541, -8.177783966,
       -8.127202988, -8.115550995, -8.110922813, -8.10451889, -8.129888535, -8.146484375, -8.163775444, -8.145051003,
       -8.106320381, -8.133347511, -8.138149261, -8.19334507, -8.214921951, -8.216370583, -8.245317459, -8.28415966,
       -8.282572746, -8.315493584, -8.357240677, -8.422780991, -8.473991394, -8.548114777, -8.6733284, -8.783385277,
       -8.925534248, -9.071006775, -9.172624588, -9.330206871, -9.480500221, -9.662128448, -9.834470749, -10.05888844,
       -10.17185688, -10.43781853, -10.57190323, -10.73662281, -10.89041901, -11.04633713, -11.19859695, -11.42281342,
       -11.58877277, -11.79301739, -11.97921753, -12.14216042, -12.30444336, -12.43070221, -12.58107185, -12.71351242,
       -12.84295654, -13.00906563, -13.17748833, -13.40923309, -13.66138458, -14.0051012, -14.35840034, -14.73783493,
       -15.13147354, -15.52887058, -15.94050407, -16.38922501, -16.8422966, -17.35690308, -17.8589077, -18.40221024,
       -18.89620781, -19.32900238, -19.76043701, -20.37581825, -20.97193146, -21.52806282, -22.21601677, -22.95506859,
       -23.78098106, -24.67673874, -25.81791878, -27.30727386, -28.96405602, -30.90691185, -33.41353226, -33.94599152,
       -33.03450394, -30.96505547, -28.57443237, -26.54086494, -24.7819519, -23.44169235, -21.97460556, -20.80608177,
       -19.73350525, -18.65771103, -17.81177711, -16.97323418, -16.19133759, -15.54279613, -14.85311508, -14.26179409,
       -13.62238121, -13.11615276, -12.63314342, -12.12530899, -11.69655514, -11.30163097, -10.90059471, -10.52633762,
       -10.13617706, -9.762444496, -9.421667099, -9.126354218, -8.830103874, -8.568763733, -8.297082901, -8.06511879,
       -7.857870102, -7.647917747, -7.412720203, -7.232706547, -7.04059124, -6.841612816, -6.661447525, -6.483736038,
       -6.297156334, -6.15134716, -6.000156403, -5.879315853, -5.736511707, -5.604342461, -6.127653122, -5.929526806,
       -5.828621864, -5.650005341, -5.552627563, -5.399239063, -5.23062849, -5.050760269, -4.94329071, -4.798144817,
       -4.64658308, -4.58951664, -4.447311401, -4.351338863, -4.222981453, -4.128682137, -4.049602509, -3.959531784,
       -3.841657639, -3.740225792, -3.639666796, -3.519000292, -3.450951099, -3.377755404, -3.310853481, -3.241042376,
       -3.158916473, -3.096710682, -3.004101753, -2.941199064, -2.865587234, -2.828384399, -2.760800123, -2.70406127,
       -2.65947628, -2.572434664, -2.493781567, -2.448805571, -2.417292356, -2.332271576, -2.300523281, -2.235235691,
       -2.17696476, -2.147727966, -2.08457756, -2.037608385, -2.030073404, -1.955549955, -1.914127111, -1.916182518,
       -1.866333723, -1.828286171, -1.800377607, -1.796028852, -1.735588551, -1.745534778, -1.707245231, -1.692732573,
       -1.691508532, -1.692862988, -1.663347006, -1.65788269, -1.639622688, -1.631232738, -1.664544463, -1.667152286,
       -1.647252083, -1.6545223, -1.634743214, -1.628013372, -1.619013548, -1.641403675, -1.654264092, -1.629508495,
       -1.628828406, -1.643304586, -1.630003333, -1.68388772, -1.641316414, -1.668212652, -1.618229628, -1.655787826,
       -1.608837366, -1.646574259, -1.635203004, -1.63406992, -1.601251006, -1.630458117, -1.602436066, -1.58801806,
       -1.614257336, -1.611077785, -1.577382088, -1.58559978, -1.588947296, -1.582833052, -1.580895066, -1.612391472,
       -1.576727271, -1.586042285, -1.589945793, -1.553916812, -1.560229301, -1.606724977, -1.56560421, -1.57322669,
       -1.596293449, -1.584367514, -1.571959615, -1.604761124, -1.567072153, -1.624849677, -1.58217454, -1.648162961,
       -1.627061129, -1.706493974, -1.642502785, -1.692834496, -1.686840177, -1.723334789, -1.744763255, -1.77798295,
       -1.807625532, -1.790100574, -1.853086948, -1.855478048, -1.892213345, -1.93426466, -1.946662903, -1.942147255,
       -1.995603085, -2.021216631, -2.051161528, -2.001528263, -2.072818279, -2.070992708, -2.100316763, -2.207594395,
       -2.180592299, -2.190364361, -2.173692942, -2.193660259, -2.21147728, -2.228121281, -2.268562794, -2.244643927,
       -2.261028767, -2.286050558, -2.301484346, -2.410764694, -2.351442814, -2.376184702, -2.357131958, -2.376286268,
       -2.415348053, -2.453021526, -2.398682356, -2.450158596, -2.401318073, -2.388048887, -2.456315279, -2.438214779,
       -2.472894907, -2.461638212, -2.534115553, -2.514077663, -2.481888056, -2.506649494, -2.520323277, -2.511511564,
       -2.525862694, -2.557298422, -2.577206612, -2.559695959, -2.571627855, -2.563164234, -2.60279417, -2.558226585,
       -2.619006872, -2.636137962, -2.573531151, -2.612449408, -2.610878944, -2.638984203, -2.646641731, -2.645757675,
       -2.668448448, -2.615818977, -2.678872824, -2.664002419, -2.712621689, -2.725452662, -2.743127346, -2.684511185,
       -2.711328268, -2.721934795, -2.737370968, -2.777047873, -2.761605263, -2.778219461, -2.805330276, -2.835128546,
       -2.841023445, -2.849072933, -2.865864038, -2.887181997, -2.924516678, -2.918622732, -2.925630569, -2.99097681,
       -2.994186163, -2.99433732, -3.063297749, -3.048479319, -3.009461403, -3.050323248, -3.069365978, -3.095424652,
       -3.09022522]


def main():
    start_time = timeit.timeit()
    start_f = 750
    stop_f = 1300
    sweep_range = stop_f - start_f
    pts = 401
    pt_f_delta = sweep_range / (pts-1)
    freq = [idx*pt_f_delta+start_f for idx in range(0, pts)]

    # freq, pow = np.asarray(freq), np.asarray(pow)
    print(len(freq), len(pow))
    # print(freq)
    # print(pow)
    delta = 0.2
    sweep_mid = start_f+(sweep_range/2)
    fitted_curve = sp.interpolate.interp1d(x=freq, y=pow, kind="cubic")
    new_xvalues = np.arange(start_f, stop_f, delta)
    new_yvalues = [fitted_curve(x) for x in new_xvalues]
    minimum_pt = sp.optimize.minimize_scalar(fitted_curve, method='bounded', bounds=(start_f, stop_f))
    # minimum_pt = sp.optimize.brute(fitted_curve, ((start_f, stop_f, 1), )))
    #print(minimum_pt)

    # peak_values_idx = list(sp.signal.argrelextrema(np.asarray(pow), np.greater)[0])
    # trough_values_idx = list(sp.signal.argrelextrema(np.asarray(pow), np.less)[0])
    # peak_values_idx = list(sp.signal.argrelextrema(np.asarray(new_yvalues), np.greater)[0])
    # trough_values_idx = list(sp.signal.argrelextrema(np.asarray(new_yvalues), np.less)[0])
    # print(type(peak_values_idx), peak_values_idx)
    # peak_values = [fitted_curve(idx*delta+start_f) for idx in peak_values_idx]
    # peak_value_freq = [idx*delta+start_f for idx in peak_values_idx]
    # trough_values = [fitted_curve(idx*delta+start_f) for idx in trough_values_idx]
    # trough_value_freq = [idx*delta+start_f for idx in peak_values_idx]

    dB_target_1 = -10
    dB_target_2 = -6
    dB_target_3 = -3
    target_cutoff_mags = [dB_target_3, dB_target_2, dB_target_1]

    # Run through the target magnitudes, placing priority on the more negative numbers
    sorted_target_magnitudes = sorted(target_cutoff_mags, reverse=True)
    is_cutoff_successful = False
    cnt_max = len(sorted_target_magnitudes)
    cnt_cur = 0

    while is_cutoff_successful is False:
        print("------------------------")
        if cnt_cur >= cnt_max:
            print("Exceeded count max. Breaking...")
            break

        target_yvalues = [target_cutoff_mags[cnt_cur] for x in new_xvalues]
        intersect_points = intersect(np.asarray(new_xvalues), np.asarray(new_yvalues), np.asarray(target_yvalues))
        intersect_points = list(intersect_points)
        print(f"For current run num. {cnt_cur}, intersect points number at {len(intersect_points)}")

        if len(intersect_points) < 2:
            print("Inadequate intersect points, jumping to next...")
            cnt_cur = cnt_cur + 1
            continue
        else:
            print(f"Getting the intersect and more for target cutoff of {target_cutoff_mags[cnt_cur]} ")
            # Get distance of intersect points to the minimum point and save as dictionary
            intersect_pt_as_list_of_dicts = list()

            for pt in intersect_points:
                print(pt)
                freq = pt[0]
                mag = pt[1]
                dist = abs(minimum_pt["x"] - freq)
                dict_update_buffer = {"freq": freq, "mag": mag, "dist": dist}
                intersect_pt_as_list_of_dicts.append(dict_update_buffer)
            #print("intersect_pt_as_list_of_dicts:", intersect_pt_as_list_of_dicts)

            # Sort by distance
            sorted_list = sorted(intersect_pt_as_list_of_dicts, key=operator.itemgetter("dist"))
            print("sorted_list:", sorted_list)

            # Use the closest points
            closest_points = [sorted_list[0], sorted_list[1]]
            print(closest_points)

            # Check whether the two points are left and right of the minimum point
            sorted_list_by_f = sorted(closest_points, key=operator.itemgetter("freq"))
            print("Sorted list by f:", sorted_list_by_f)

            if not ((sorted_list_by_f[0]["freq"] < minimum_pt["x"]) and (minimum_pt["x"] < sorted_list_by_f[1]["freq"])):
                print("Does not match criteria of two points being left and right")
                cnt_cur = cnt_cur + 1
                continue

            # Get bandwidth
            bandwidth = abs(closest_points[0]["freq"] - closest_points[1]["freq"])

            # Get Q factor
            q_factor = minimum_pt["x"] / bandwidth

            print("Bandwidth:", bandwidth, "Q Factor:", q_factor)
            end_time = timeit.timeit()
            time_elapsed = end_time - start_time
            print("Time elapsed for this iteration:", float(time_elapsed))

            is_cutoff_successful = True

    print("Target found:", is_cutoff_successful)
    # plt.plot(freq, pow, marker=".", label='Original', color="r", alpha=0.5)
    plt.plot(new_xvalues, fitted_curve(new_xvalues), label='Interpolated', color="m", alpha=0.5)
    # plt.plot(peak_values, fitted_curve(peak_values), marker="+")
    # plt.plot(trough_values, fitted_curve(trough_values), marker="+")
    # plt.plot(peak_value_freq, peak_values, marker="+")
    # plt.plot(trough_value_freq, tro ugh_values, marker="+")
    plt.plot(minimum_pt["x"], fitted_curve(minimum_pt["x"]), marker="x")
    plt.legend()
    plt.show()


def intersect(x: np.array, f: np.array, g: np.array) -> Iterable[Tuple[(int, int)]]:
    """
    Finds the intersection points between `f` and `g` on the domain `x`.
    Given:
        - `x`: The discretised domain.
        - `f`: The discretised values of the first function calculated on the
               discretised domain.
        - `g`: The discretised values of the second function calculated on the
               discretised domain.
    Returns:
        An iterable containing the (x,y) points of intersection.
    """
    idx = np.argwhere(np.diff(np.sign(f - g))).flatten()
    return zip(x[idx], f[idx])

if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
