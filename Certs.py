import ipaddress
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from datetime import datetime, timedelta
import time
"""
Mosquito config file : mosquittoCryptography.conf
Cd C:\Program Files\mosquitto
mosquitto –v -c ”mosquittoCryptography.conf”

"""
print("HTTPs certficate: \n-generate CA ( Comon name 'MyCa'),add CA to Windows certificates (Press WINDOWS+R and open certmgr.msc) \n-generate server certificate ( Common name and Alt name - AL1590 ip address), put server cert and server key to AL1590 HTTPS page")
print("MQTTs certficate: \n-generate CA\n-generate server certificate ( Comon name and Alt name must be broker IP address), \n modify broker config file and copy server cert, key and CA to broker cert localization\n-generate client certificate ( Common name and Alt name - AL1590 ip address)\n put certificate and key to MQTTs page, CA if certificate validation needed,\n install client certificate and key and CA for MQTT Explorer")
print("OPC ua certficate: \n-generate self signed client certificate ( Common name and Alt name - AL1590 ip address, URI:urn:opcua:uaexpert:client ), put certificate and key to AL1590 OPC UA page, turn on Security profiles ")
print("If You want to use certificate validation, set device time! ")
# ============================
# 1. GENEROWANIE KLUCZA CA
# ============================
def certGen():

    tpx=input("Generate CA certificate [y=yes , n =no]?")
    if tpx == "y":
        ca_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        print("CA private key created")
        CON="PL"
        SOR="Opolskie"
        LN="Opole"
        ORN="Ifm"
        CN="MyCA"
        subject={"COUNTRY_NAME":CON,
                 "STATE_OR_PROVINCE_NAME": SOR,
                 "LOCALITY_NAME": LN,
                 "ORGANIZATION_NAME":ORN,
                 "COMMON_NAME":CN}
        for n,v in subject.items():
            subject[n]  = input(f"CA: Type {n} [{v}]: ") or v
        print(f"Subject:{subject}")




        ca_subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, subject["COUNTRY_NAME"]),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, subject["STATE_OR_PROVINCE_NAME"]),
            x509.NameAttribute(NameOID.LOCALITY_NAME, subject["LOCALITY_NAME"]),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, subject["ORGANIZATION_NAME"]),
            x509.NameAttribute(NameOID.COMMON_NAME, subject["COMMON_NAME"]),
        ])

        ca_cert = (
            x509.CertificateBuilder()
            .subject_name(ca_subject)
            .issuer_name(ca_subject)
            .public_key(ca_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=3650))
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=False,
                    key_encipherment=False,
                    key_cert_sign=True,
                    crl_sign=True,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False
                ),

                critical=True
            )
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
                critical=False,
            )
            .sign(private_key=ca_key, algorithm=hashes.SHA256())
        )


        with open("ca_key.pem", "wb") as f:
            f.write(
                ca_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
        print("CA public key created")

        with open("ca_cert.pem", "wb") as f:
            f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
        print("CA cert created")
    else:
        print("CA not created")

    # ============================
    # 2. GENEROWANIE KLUCZA SERWERA
    # ============================
    tpx = input("Generate server certificate [y=yes , n =no]?")
    if tpx == "y":
        server_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        print("Server key created")
        CON="PL"
        SOR="Opolskie"
        LN="Opole"
        ORN="Ifm"
        CN="192.168.5.10"
        ALN="192.168.5.10"
        subject={"COUNTRY_NAME":CON,
                 "STATE_OR_PROVINCE_NAME": SOR,
                 "LOCALITY_NAME": LN,
                 "ORGANIZATION_NAME":ORN,
                 "COMMON_NAME":CN,
                 "ALT_NAME":ALN}
        for n,v in subject.items():
            subject[n] = input(f"Type {n} [{v}]: ") or v
            time.sleep(0.5)
        print(f"Subject:{subject}")

        server_subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, subject["COUNTRY_NAME"]),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, subject["STATE_OR_PROVINCE_NAME"]),
            x509.NameAttribute(NameOID.LOCALITY_NAME, subject["LOCALITY_NAME"]),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, subject["ORGANIZATION_NAME"]),
            x509.NameAttribute(NameOID.COMMON_NAME, subject["COMMON_NAME"]),

        ])

        alt_names = [
            #x509.DNSName("example.com"),
            #x509.DNSName("www.example.com"),
            x509.IPAddress(ipaddress.IPv4Address(subject["ALT_NAME"]))
        ]

        csr = (
            x509.CertificateSigningRequestBuilder()
            .subject_name(server_subject)
            .add_extension(
                x509.SubjectAlternativeName(alt_names),
                critical=False
            )
            .sign(server_key, hashes.SHA256())
        )

        with open("server.csr.pem", "wb") as f:
            f.write(csr.public_bytes(serialization.Encoding.PEM))


        server_cert = (

            x509.CertificateBuilder()
            .subject_name(csr.subject)
            .issuer_name(ca_cert.subject)
            .public_key(csr.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=825))
            .add_extension(
                x509.SubjectAlternativeName(alt_names),
                critical=False,
                )
            .add_extension(
                x509.KeyUsage(True,False,True,False,True,False,False,True,False),
            critical=False
            )
            .add_extension(
                x509.ExtendedKeyUsage([x509.ExtendedKeyUsageOID.SERVER_AUTH]),
                critical=False
            )
            .add_extension(
                x509.BasicConstraints(False,None),
                critical=False
            )
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(server_key.public_key()),
                critical=False,
            )
            .add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
                critical = False
            )

            .sign(private_key=ca_key, algorithm=hashes.SHA256())
        )

        with open("server_key.pem", "wb") as f:
            f.write(
                server_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
        print("Server public key created")
        with open("server_cert.pem", "wb") as f:
            f.write(server_cert.public_bytes(serialization.Encoding.PEM))
        print("Server certificate created")
    else:
        print("Server certificate not created")
        print("zmiana")
    # ============================
    # 4. CERTYFIKAT KLIENTA (mTLS)
    # ============================

    name="client"
    opc_ua=False
    tpx = input("Generate client certificate [y=yes , n =no]?")
    if tpx == "y":
        name = input(f"Type name of certificate: or press enter for default {name}")or name
        x = input(f"Opc-ua certificate? [y=yes , n =no]")
        if x == "y":
            opc_ua = True

        client_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        print("Client private key created")
        CON = "PL"
        SOR = "Opolskie"
        LN = "Opole"
        ORN = "Ifm"
        CN = "192.168.5.151"
        ALN = "192.168.5.151"
        ALN_URI="urn:ifm-al1590-000260700181:OPCUA-Server_IoTCore"
        subject = {"COUNTRY_NAME": CON,
                   "STATE_OR_PROVINCE_NAME": SOR,
                   "LOCALITY_NAME": LN,
                   "ORGANIZATION_NAME": ORN,
                   "COMMON_NAME": CN,
                   "ALT_NAME": ALN,
                   "APlication URI:": ALN_URI}
        for n, v in subject.items():
            subject[n]  = input(f"Type {n} [{v}]: ") or v
            time.sleep(0.5)
        print(f"Subject:{subject}")

        client_subject=issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, subject["COUNTRY_NAME"]),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, subject["STATE_OR_PROVINCE_NAME"]),
            x509.NameAttribute(NameOID.LOCALITY_NAME, subject["LOCALITY_NAME"]),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, subject["ORGANIZATION_NAME"]),
            x509.NameAttribute(NameOID.COMMON_NAME, subject["COMMON_NAME"]),
        ])
        if opc_ua:
            alt_names=[x509.UniformResourceIdentifier(subject["APlication URI:"]),x509.IPAddress(ipaddress.IPv4Address(subject["ALT_NAME"]))]
            ext_key_use=[x509.ExtendedKeyUsageOID.CLIENT_AUTH,x509.ExtendedKeyUsageOID.SERVER_AUTH]
            authorityKeyIdentifier=client_key.public_key()
            sign=client_key
            cert_encoding=serialization.Encoding.DER
            cert_ext="der"
            cert_issuer=issuer

        else:
            alt_names=[x509.IPAddress(ipaddress.IPv4Address(subject["ALT_NAME"]))]
            ext_key_use=[x509.ExtendedKeyUsageOID.CLIENT_AUTH]
            authorityKeyIdentifier=ca_key.public_key()
            sign=ca_key
            cert_encoding=serialization.Encoding.PEM
            cert_ext="pem"
            cert_issuer=ca_cert.subject

        client_csr = (
            x509.CertificateSigningRequestBuilder()
            .subject_name(client_subject)
            .add_extension(
                x509.SubjectAlternativeName(alt_names),
                critical=False
            )
            .sign(client_key, hashes.SHA256())
        )

        with open(f"{name}.csr.pem", "wb") as f:
            f.write(client_csr.public_bytes(serialization.Encoding.PEM))



        if opc_ua:
            client_cert = (
                x509.CertificateBuilder()
                .subject_name(client_csr.subject)
                # .issuer_name(ca_cert.subject)
                .issuer_name(cert_issuer)
                .public_key(client_csr.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.utcnow())
                .not_valid_after(datetime.utcnow() + timedelta(days=825))
                .add_extension(
                    x509.SubjectAlternativeName(alt_names),
                    critical=False
                )
                .add_extension(
                    x509.ExtendedKeyUsage(ext_key_use),
                    critical=False
                )

                .add_extension(
                    x509.KeyUsage(True, True, True, True, False, True, False, False, False),
                    critical=False
                )
                .add_extension(
                    x509.BasicConstraints(False, None),
                    critical=False
                )
                .add_extension(
                    x509.SubjectKeyIdentifier.from_public_key(client_key.public_key()),
                    critical=False,
                )
                .add_extension(
                    x509.AuthorityKeyIdentifier.from_issuer_public_key(authorityKeyIdentifier),
                    critical=False
                )
                # .sign(private_key=ca_key, algorithm=hashes.SHA256())
                .sign(private_key=sign, algorithm=hashes.SHA256())
            )
            k = input("PFX key format - type pfx, if PEM format press ENTER")
            if k=="pfx":

                data = pkcs12.serialize_key_and_certificates(
                    name=b"client1",  # alias w PFX
                    key=client_key,  # klucz prywatny
                    cert=client_cert,  # certyfikat
                    cas=None,  # łańcuch CA (jeśli jest)
                    encryption_algorithm=serialization.NoEncryption()
                )
                key_ext="pfx"
            else:
                key_ext = "pem"
                data = client_key.private_bytes(
                encoding = serialization.Encoding.PEM,
                format = serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm = serialization.NoEncryption()
                )
        else:
            client_cert = (
                x509.CertificateBuilder()
                .subject_name(client_csr.subject)
                # .issuer_name(ca_cert.subject)
                .issuer_name(cert_issuer)
                .public_key(client_csr.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.utcnow())
                .not_valid_after(datetime.utcnow() + timedelta(days=825))
                .add_extension(
                    x509.SubjectAlternativeName(alt_names),
                    critical=False
                )
                .add_extension(
                    x509.ExtendedKeyUsage(ext_key_use),
                    critical=False
                )

                .add_extension(
                    x509.KeyUsage(True, False, True, False, True, False, False, True, False),
                    critical=False
                )
                .add_extension(
                    x509.BasicConstraints(False, None),
                    critical=False
                )
                .add_extension(
                    x509.SubjectKeyIdentifier.from_public_key(client_key.public_key()),
                    critical=False,
                )
                .add_extension(
                    x509.AuthorityKeyIdentifier.from_issuer_public_key(authorityKeyIdentifier),
                    critical=False
                )
                # .sign(private_key=ca_key, algorithm=hashes.SHA256())
                .sign(private_key=sign, algorithm=hashes.SHA256())
            )
            key_ext="pem"
            data=client_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                )
        with open(f"{name}_key.{key_ext}", "wb") as f:
            f.write(data)
        print("Client public key created")


        with open(f"{name}_cert.{cert_ext}", "wb") as f:
            f.write(client_cert.public_bytes(cert_encoding))
        print("Client certificate created")
    else:
        print("Client certificate not created")

certGen()
