import numpy as np
from skimage import color, io
import math
import matplotlib.pyplot as plt

def load(fname):
    '''
    Load Image from path
    Args:
        fname: string of path to image
    Returns:
        image: numpy array of corrected values
    '''
    image = io.imread(fname)
    image = image.astype(np.float64)
    return image

def save(image, fname):
    '''
    Save Image to Directory
    Args:
        image: numpy array of shape (imageheight, imagewidth)
        fname: string name of file 
    Returns:
    '''
    image = (image).astype(np.uint8)
    io.imsave(fname, image, check_contrast=False)
    return

#Extracting Channels
def extract_red(image):
    '''
    Extract Red Pixels from Image
    Args:
        image: numpy array of shape (imageheight, imagewidth, 3)

    Returns:
        red_image: numpy array of shape (imageheight, imagewidth)
    '''
    imagecopy = np.copy(image)
    imagecopy[:,:,1] = 0
    imagecopy[:,:,2] = 0
    red_image = imagecopy[:,:,0]
    return red_image

def extract_green(image):
    '''
    Extract Green Pixels from Image
    Args:
        image: numpy array of shape (imageheight, imagewidth, 3)

    Returns:
        green_image: numpy array of shape (imageheight, imagewidth)
    '''
    imagecopy = np.copy(image)
    imagecopy[:,:,0] = 0
    imagecopy[:,:,2] = 0
    green_image = imagecopy[:,:,1]
    return green_image

def overlap(ref, temp, shift):
    '''
    Cuts out the overlapping region of the temp and ref with specified shift in xdirection up to 41 moves
    Args:
        ref: reference image or fixed image
        temp: template image or moving image
        shift: xdirection shift by pixel number
    Returns:
        result: overlapping region of ref and temp
    '''
    result = np.copy(ref)
    dim = np.shape(result)
    for i in range(dim[0]):
        for j in range(dim[1]):
            xmin = (40-shift) + j
            result[i][j] = temp[i][xmin]
    return result

def prepare_image(image):
    '''
    Extracts red and green channels and crops 20 pixels from the right and left of the green channel image
    Args:
        image: input grayscale RGB image
    Returns:
        green: cropped green channel
        red: red channel
    '''
    green = extract_green(image)
    red = extract_red(image)
    for _ in range(20):
        green = np.delete(green, 0, 1) #First Column
        green = np.delete(green, -1, 1) #Last Column
    return green, red

def marginal_pmf(image, bin_size, id0):
    '''
    Create Histogram for Probability of each Grey Value
    Args:
        image: numpy array of shape (imageheight, imagewidth)
        bin_size: how many neighbouring grey values to consider the same

    Returns:
        green_image: numpy array of shape (imageheight, imagewidth)
    '''
    hist_vals = np.zeros(256)
    count = 0
    for row in image:
        for i in range(len(row)):
            pix = int(row[i])
            hist_vals[pix] += 1
            count += 1
    i = 0
    hist_result = []
    for i in range(0, 255, bin_size):
        var = 0
        for j in range(bin_size):
            var += hist_vals[i+j]
        hist_result.append(var / count)
        i = i * bin_size
    return hist_result

def joint_pmf(x_pmf, y_pmf):
    '''
    Produces the Normalized 2D Histogram 
    Args:
        x_pmf: 1D Normalized Histogram of Reference Image
        y_pmf: 1D Normalized Histogram of Template Image

    Returns:
        hist_result: The 2D Normalized Histogram
    '''
    nrow = len(x_pmf)
    ncol = len(y_pmf)
    hist_result = np.zeros((nrow, ncol))
    track = 0
    for i in range(nrow):
        for j in range(ncol):
            hist_result[i, j] = x_pmf[i] + y_pmf[j]
    hist_result = hist_result / np.sum(hist_result)
    return hist_result

def mutual_information(image1, image2, id0, bin_size=1):
    '''
    Calculates the Mutual Information between the inputs
    Args:
        image1: reference image
        image2: template image
        id0: identifier for histogram plots
        bin_size=1: Number of neighbouring grey values to consider the same

    Returns:
        result: A value for the mutual information according to EQ1
    '''
    px = marginal_pmf(image1, bin_size, id0)
    py = marginal_pmf(image2, bin_size, id0+100)
    pxy = joint_pmf(px, py)
    mutual_information = 0
    visual = np.copy(pxy)
    for i in range(len(px)):
        for j in range(len(py)):
            var1 = px[i] * py[j]
            var2 = pxy[i, j] / var1
            partial = pxy[i, j] * math.log(var2, 2)
            visual[i,j] = partial
            mutual_information += partial
    #plt.imshow(visual, cmap='gray')
    #fn = 'mi_' + str(id0) + '.png'
    #plt.savefig(fn)
    #plt.clf()
    return mutual_information

def registration(image):
    reference, template = prepare_image(image)
    save(reference, 'ref.png')
    save(template, 'temp.png')
    results = []
    for i in range(41):
        overlappingregion = overlap(reference, template, i)
        MI = mutual_information(reference, overlappingregion, i, bin_size=3)
        results.append(MI)
    return results

test = load('../input/test3.jpeg')

'''
#Gaussian Noise Addition
row,col,ch= test.shape
mean = 0
var = 0.1
sigma = var**0.5
gauss = np.random.normal(mean,sigma,(row,col,ch))
gauss = gauss.reshape(row,col,ch)
noisy = test + gauss - 1
save(noisy, 'gauss_noise3.png')
''' 
# comment out the above block to obtain experimental results

values = registration(noisy)
print(values)
print(np.min(values), np.argmin(values))
plt.plot(values)
plt.xlabel("Shift in X Direction")
plt.ylabel("Mutual Information")
plt.savefig("../output/mi_plot4_bin_255.png")
plt.clf()
'''
Image 1 Results: 
    values: [0.9208992008321772, 0.9216674192767316, 0.9226925473169687, 0.9236530943068013, 0.9245944102082683, 0.9253195208875502, 0.9259800799097523, 0.9267518801815103, 0.9273534419521324, 0.92815607960689, 0.929206510635319, 0.9302752817745638, 0.9314631751394911, 0.9322023325769789, 0.9331031779934744, 0.9340157989399234, 0.9349048829427431, 0.9356536957137305, 0.9364845976835522, 0.9373659309028057, 0.9381289870348896, 0.9390152455502615, 0.940014734791387, 0.9406852031892886, 0.9412706927191858, 0.94183001623625, 0.94233069313878, 0.9427083721643773, 0.9430443102729951, 0.9433854839916053, 0.9437440616191268, 0.9442443506439835, 0.9444993361218221, 0.9447610928783307, 0.944948547884882, 0.9451151774989712, 0.9453340376252298, 0.9455893577008757, 0.9458764827769989, 0.9459383529162547, 0.9459331251996006]
    min(MI): 0.9208992008321772, Shift: 0

Image 2 Results: 
    values: [0.9131260746167476, 0.9152247521104938, 0.9166810201893607, 0.9179513410429341, 0.9180053443141181, 0.9176770189766017, 0.9176179666066615, 0.9174213178953887, 0.9172629110321635, 0.9171926396929597, 0.9166549956670547, 0.9174029764584131, 0.9177411151569334, 0.9179106659812365, 0.9180217903550861, 0.9187457074762259, 0.9194326359925225, 0.92029557098961, 0.9206363413856425, 0.9215832614669913, 0.9222633095750807, 0.9229082182603653, 0.9238561670286894, 0.9250882908319934, 0.925513274358075, 0.9259778152142117, 0.9270151043403915, 0.9270412194476626, 0.9272488538951477, 0.9278123193883349, 0.9272556018652424, 0.925925745789333, 0.9257314818588188, 0.9260360300130377, 0.9260646493891227, 0.9262349474736586, 0.9264925084756295, 0.927077628400063, 0.9278506347873262, 0.928028039262585, 0.9283307248557549]
    min(MI): 0.9131260746167476, Shift: 0

Image 3 Results: 
    values: [0.190714923153389, 0.18981970690059277, 0.18952880350091172, 0.1894917499095629, 0.1895538513328542, 0.18936496646311307, 0.18908316871318268, 0.1888114227514952, 0.1885112113753243, 0.18809674308876764, 0.18773690430891476, 0.18741556376031288, 0.18731037835009137, 0.18712934445719803, 0.1869108478854437, 0.18697822305344045, 0.18726743820651234, 0.18749481055628198, 0.18748125138418992, 0.18735190356275438, 0.187467626641609, 0.18762833988693317, 0.18772326674175197, 0.1877037911603487, 0.18789441658776243, 0.18808300591782245, 0.18780669377966921, 0.18789418816931394, 0.18790344349960125, 0.1881608445853937, 0.18809144252594287, 0.1880379214334311, 0.18775507296976765, 0.18757417017132802, 0.1874989519136214, 0.18779171857202354, 0.18806564846530774, 0.18881642739415638, 0.18922387350285289, 0.18950977932864338, 0.1893999885763844]
    min(MI): 0.1869108478854437, Shift: 14

Image 4 (Image 3 with Gaussian Noise) Results: 
    values: [0.13995604476990245, 0.13902480184114221, 0.1386398609148664, 0.13838273608683582, 0.13808499066021773, 0.13771505937669756, 0.1373612755724599, 0.13716774298481046, 0.1368082879778111, 0.13634896179237044, 0.13600863798228224, 0.135739870040355, 0.13564529503553202, 0.13543511173338255, 0.13525419625292165, 0.13522216878183274, 0.1353894740610859, 0.135554518552575, 0.13553185093815148, 0.13533269379010893, 0.13544645920035, 0.1354100711296137, 0.13550502574897463, 0.1356307817091898, 0.13587214916415052, 0.13592839691071146, 0.13570397161776399, 0.13586924915988768, 0.13581757961913227, 0.13611836565305743, 0.1361263349887397, 0.13600014977140157, 0.13580543930434977, 0.13573932997394264, 0.13552257277041196, 0.13569982056810864, 0.1360357256650076, 0.13662165253819566, 0.13685236404165455, 0.1370500563026714, 0.13700341417418682]
    min(MI): 0.13522216878183274, Shift: 15, bin_size= 1

    values: [0.16013469893393187, 0.15930744457262713, 0.15897050661368844, 0.15889594590907208, 0.15863884459215777, 0.15829959638152954, 0.15793904197493458, 0.15763794753717383, 0.15732107531042627, 0.15687491749061835, 0.1565306408058746, 0.15618271470043965, 0.15606124728372725, 0.15587299360542628, 0.15566759387115267, 0.15569893561899065, 0.15597366851714958, 0.1561474930344279, 0.1561577062714501, 0.15603856679511233, 0.15619809069597348, 0.15626605799814705, 0.15636631584553484, 0.15643969009738373, 0.15676483672197788, 0.1569341120557956, 0.15665537148585315, 0.1567398130770288, 0.15680361425495257, 0.1570442229013545, 0.157088669075455, 0.15705074251570605, 0.15675420973850904, 0.15662811702416551, 0.15641548546895528, 0.15656667655944387, 0.15680263818150436, 0.15748993298249161, 0.15788764979702133, 0.15818558870627786, 0.15807167195091468]
    min(MI): 0.15566759387115267, Shift: 14, bin_size= 3

    values: [0.12952057859329144, 0.12870458598656187, 0.1284160311222728, 0.1281525251387147, 0.12784545776971085, 0.12758413984604108, 0.12732180554672323, 0.12704615370583597, 0.1266948003581067, 0.12625114575907817, 0.1259182876914811, 0.12571191378869367, 0.12555943681339748, 0.12536588151981487, 0.125150212484791, 0.1251525760433729, 0.12551873803507535, 0.1257228478516812, 0.12557770839485385, 0.1254871380480393, 0.12565296490236488, 0.1256892826164564, 0.12579408678008352, 0.1257096478049994, 0.12595482730109836, 0.12602911516554122, 0.12581225547084082, 0.1258817777002208, 0.1259474110888688, 0.12637874348365352, 0.12627404734056488, 0.12630611024613483, 0.1261752442633671, 0.12592829347947068, 0.12573937079744446, 0.12590940248721746, 0.12617336775770646, 0.126569825319792, 0.12690367614017978, 0.12710903461460993, 0.12697943616185714]
    min(MI): 0.125150212484791, Shift: 14, bin_size= 5

    values: [0.12053149893134865, 0.11982005139370006, 0.11938853767552574, 0.1190951687616678, 0.11872650663957172, 0.1184811512998673, 0.1182731390165798, 0.11799622633518096, 0.11778942395397898, 0.11736404317759402, 0.11706512311052736, 0.11677141235349293, 0.11648593500735312, 0.11638157781348318, 0.11616028580201969, 0.11607814121861532, 0.11633146406763355, 0.11641638475503274, 0.11629403818004541, 0.11623966114858893, 0.11639632062504845, 0.11623391098135796, 0.11631645522586556, 0.116265643664089, 0.11640415916160278, 0.11649118970382236, 0.11628587635335709, 0.11633247446343695, 0.11631687058977992, 0.11653296410985531, 0.1165852964161839, 0.11668335709746666, 0.11660996929988869, 0.11637440547226138, 0.11624137800781213, 0.11642198713773552, 0.11663653603929572, 0.11698245081549193, 0.1173187254909696, 0.1175664367487308, 0.11739595152930206]
    min(MI): 0.11607814121861532, Shift: 15, bin_size= 15

    values: [0.1170073666771375, 0.1162756906254696, 0.11585554102532174, 0.1156171300364812, 0.1152807446582158, 0.11497864834554496, 0.11469275774612206, 0.11436342514117477, 0.11408553260365105, 0.11363778284920299, 0.11328520054923208, 0.11277254470391626, 0.11253126306543142, 0.11243640953467551, 0.1121650262416704, 0.11204783520502307, 0.11226928645513722, 0.11243739844145466, 0.11228973155698031, 0.11214425886287267, 0.11223410646398474, 0.11216550768154437, 0.11225327385586403, 0.11223477524797842, 0.11238722497914279, 0.11234973301663062, 0.11209597323311123, 0.11227206616767438, 0.11238949082711847, 0.11255959401226345, 0.11269793731001711, 0.11296562623777569, 0.11288507915347683, 0.11264007942938288, 0.11244442982461146, 0.11252662293241855, 0.1127732768771241, 0.11321974024574308, 0.11344003631204319, 0.11356501655569039, 0.11342184269257698]
    min(MI): 0.11204783520502307, Shift: 15, bin_size= 17

    values: [0.03302828397948376, 0.032612508476602485, 0.032379608610532004, 0.03220190900637277, 0.03199985341584419, 0.031878388494907324, 0.03175025700150529, 0.03159674075106124, 0.031383876787385676, 0.03118283633715532, 0.03091969863182987, 0.030727983375947378, 0.030535130971499576, 0.03038787069275161, 0.030247266165347547, 0.030130026120263574, 0.03006428587827774, 0.0300107726169051, 0.029885494681386446, 0.029682024723617136, 0.029607642087840464, 0.02952196226525187, 0.02951587994830852, 0.029552242927183295, 0.02955316872422709, 0.029632776581382882, 0.02963522456664476, 0.029666935071650437, 0.029694572569665803, 0.02968486436690323, 0.029627406263624503, 0.02953284482839589, 0.02949964354617967, 0.029401746163294686, 0.029433311286266074, 0.029517040768111055, 0.02949467004671062, 0.029447648603891704, 0.029483309205782182, 0.029513793494675047, 0.029445434373064832]
    min(MI): 0.029401746163294686, Shift: 33, bin_size= 51

    values: [0.02240574542499945, 0.022104306036268687, 0.021876726558766005, 0.021625478131747575, 0.021377209584704612, 0.0211709022950331, 0.021017376715714596, 0.02084250171838773, 0.020683812195940923, 0.020489726819539943, 0.020306998212029276, 0.020196191983947266, 0.020037830930156653, 0.01987816482210969, 0.019755562925754203, 0.019661182754220734, 0.0196618807573031, 0.019663194441748154, 0.019630094125807067, 0.019506712943678547, 0.01943670497695954, 0.019358339950194398, 0.019312923439155992, 0.019311471007546023, 0.01927837476706403, 0.019219675495260408, 0.019190975575434803, 0.019141156754521143, 0.019071538550786755, 0.018939388395665717, 0.018865807929369698, 0.01881608959941717, 0.018742712877666733, 0.018700534341337345, 0.018679191184559345, 0.01866013839290919, 0.018599529419542207, 0.018531841481476668, 0.018555171751018264, 0.018596005943389036, 0.018649248220769805]
    min(MI): 0.018531841481476668, Shift: 37, bin_size= 85

    values: [0.0014561429684835443, 0.0014561429684835443, 0.0014561429684835443, 0.0014561429684835443, 0.0014561429684835443, 0.0014561429684835443, 0.0014561429684835443, 0.0014561429684835443, 0.0014561429684835443, 0.0014561429684835443, 0.0014561429684835443, 0.001490828557360416, 0.001490828557360416, 0.001490828557360416, 0.001490828557360416, 0.0014561429684835443, 0.0014214582135051324, 0.0014214582135051324, 0.0014214582135051324, 0.0013867742923847235, 0.0013867742923847235, 0.0013867742923847235, 0.0013867742923847235, 0.0014214582135051324, 0.0014214582135051324, 0.0014214582135051324, 0.0014214582135051324, 0.0014214582135051324, 0.0014561429684835443, 0.0014214582135051324, 0.0013867742923847235, 0.0013867742923847235, 0.0013867742923847235, 0.0013867742923847235, 0.0013867742923847235, 0.0013867742923847235, 0.0013867742923847235, 0.0013174089515589201, 0.0013174089515589201, 0.001282727531772887, 0.001282727531772887]
    min(MI): 0.001282727531772887, Shift: 39, bin_size= 255

'''