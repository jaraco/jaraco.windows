from win32com.client import gencache, Dispatch
import win32com.client

clsid = '884e2049-217d-11da-b2a4-000e7bbb2b09'
gencache.EnsureModule('{%s}' % clsid, 0, 1, 0)

class_factory = Dispatch("X509Enrollment.CX509EnrollmentWebClassFactory")
enrollment = class_factory.CreateObject("X509Enrollment.CX509Enrollment")
pkcs10_request = class_factory.CreateObject(
    "X509Enrollment.CX509CertificateRequestPkcs10"
)
private_key = class_factory.CreateObject("X509Enrollment.CX509privateKey")
distinguished_name = class_factory.CreateObject("X509Enrollment.CX500DistinguishedName")


def generate_request():
    generate_key(length=2048)

    CONTEXT_USER = 1
    CONEXT_MACHINE = 2
    XCN_CERT_NAME_STR_NONE = 0

    hresult = pkcs10_request.InitializeFromPrivateKey(CONTEXT_USER, private_key, "")
    name = 'CN=StartCom Free Certificate Member'
    distinguished_name.Encode(name, XCN_CERT_NAME_STR_NONE)
    pkcs10_request.Subject = distinguished_name


def generate_key(length):
    key = private_key

    XCN_NCRYPT_ALLOW_EXPORT_FLAG = 1
    XCN_NCRYPT_UI_NO_PROTECTION_FLAG = 0
    XCN_NCRYPT_UI_PROTECT_KEY_FLAG = 1

    key.ProviderName = "Microsoft Enhanced RSA and AES Cryptographic Provider"
    key.ProviderType = "24"
    key.KeySpec = "1"
    key.KeyProtection = XCN_NCRYPT_UI_NO_PROTECTION_FLAG
    key.ExportPolicy = XCN_NCRYPT_ALLOW_EXPORT_FLAG
    key.Length = length


generate_request()
enrollment.InitializeFromRequest(pkcs10_request)
print 'Request'
print enrollment.createRequest(1)
