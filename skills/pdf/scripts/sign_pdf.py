#!/usr/bin/env python3
"""
PDF Digital Signature Script - PDF 数字签名

支持：
- 添加数字签名（使用 X.509 证书）
- 创建可见/不可见签名
- 支持时间戳服务
- 支持多种签名算法（RSA, ECDSA）

依赖: endesive, cryptography, pyHanko
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa, ec
    from cryptography.x509 import load_pem_x509_certificate
except ImportError:
    print("错误: 缺少 cryptography 库")
    print("请运行: pip install cryptography")
    sys.exit(1)

try:
    from endesive.pdf import cms
except ImportError:
    print("错误: 缺少 endesive 库")
    print("请运行: pip install endesive")
    sys.exit(1)


# ============================================================
# 签名信息数据类
# ============================================================

class SignatureInfo:
    """签名信息容器"""

    def __init__(self):
        self.signer_name: str = ""
        self.signer_email: str = ""
        self.signing_time: Optional[datetime] = None
        self.issuer: str = ""
        self.serial_number: str = ""
        self.algorithm: str = ""
        self.is_valid: bool = False
        self.is_trusted: bool = False
        self.error_message: str = ""
        self.signature_type: str = ""
        self.location: str = ""
        self.reason: str = ""

    def __repr__(self) -> str:
        return (
            f"SignatureInfo(signer='{self.signer_name}', "
            f"valid={self.is_valid}, time={self.signing_time})"
        )


# ============================================================
# 证书加载工具
# ============================================================

def load_certificate(cert_path: str) -> bytes:
    """
    加载证书文件（PEM 或 DER 格式）。

    Args:
        cert_path: 证书文件路径

    Returns:
        证书内容（字节）
    """
    path = Path(cert_path)
    if not path.exists():
        raise FileNotFoundError(f"证书文件不存在: {cert_path}")

    with open(path, 'rb') as f:
        return f.read()


def load_private_key(key_path: str, password: Optional[str] = None) -> bytes:
    """
    加载私钥文件。

    Args:
        key_path: 私钥文件路径
        password: 私钥密码（可选）

    Returns:
        私钥内容（字节）
    """
    path = Path(key_path)
    if not path.exists():
        raise FileNotFoundError(f"私钥文件不存在: {key_path}")

    with open(path, 'rb') as f:
        return f.read()


def load_pkcs12(p12_path: str, password: str) -> tuple:
    """
    加载 PKCS#12 (.p12/.pfx) 文件。

    Args:
        p12_path: PKCS#12 文件路径
        password: 文件密码

    Returns:
        (私钥, 证书链, ) 元组
    """
    from cryptography.hazmat.primitives.serialization import pkcs12

    path = Path(p12_path)
    if not path.exists():
        raise FileNotFoundError(f"PKCS#12 文件不存在: {p12_path}")

    with open(path, 'rb') as f:
        p12_data = f.read()

    private_key, certificate, chain = pkcs12.load_key_and_certificates(
        p12_data,
        password.encode() if password else None
    )

    return private_key, certificate, chain


# ============================================================
# 签名添加功能
# ============================================================

def sign_pdf(
    input_file: str,
    output_file: str,
    cert_path: str,
    key_path: str,
    key_password: Optional[str] = None,
    reason: str = "Document signed",
    location: str = "",
    contact_info: str = "",
    visible: bool = False,
    page: int = 0,
    box: tuple = (0, 0, 0, 0),
    image_path: Optional[str] = None,
    timestamp_server: Optional[str] = None,
    digest_algorithm: str = "sha256",
    verbose: bool = False
) -> bool:
    """
    对 PDF 文件进行数字签名。

    Args:
        input_file: 输入 PDF 文件路径
        output_file: 输出 PDF 文件路径
        cert_path: 证书文件路径（PEM 格式）
        key_path: 私钥文件路径（PEM 格式）
        key_password: 私钥密码（可选）
        reason: 签名原因
        location: 签名地点
        contact_info: 联系信息
        visible: 是否创建可见签名
        page: 签名页码（0-indexed）
        box: 签名框位置 (x, y, width, height)
        image_path: 签名图片路径（可选）
        timestamp_server: 时间戳服务器 URL（可选）
        digest_algorithm: 摘要算法（sha1, sha256, sha384, sha512）
        verbose: 详细输出模式

    Returns:
        bool: 签名是否成功
    """
    try:
        # 加载证书和私钥
        cert_data = load_certificate(cert_path)
        key_data = load_private_key(key_path, key_password)

        # 读取 PDF 文件
        with open(input_file, 'rb') as f:
            pdf_data = f.read()

        if verbose:
            print(f"输入文件: {input_file}")
            print(f"证书文件: {cert_path}")
            print(f"签名原因: {reason}")
            print(f"摘要算法: {digest_algorithm}")

        # 构建签名参数
        signature_params = {
            'signature': key_data,
            'certificate': cert_data,
            'reason': reason,
            'location': location,
            'contact': contact_info,
            'signingtime': datetime.utcnow(),
            'algorithm': digest_algorithm,
        }

        # 添加可见签名框
        if visible and box != (0, 0, 0, 0):
            signature_params['signaturebox'] = box
            signature_params['signaturepage'] = page

            # 添加签名图片
            if image_path:
                with open(image_path, 'rb') as f:
                    signature_params['signatureimage'] = f.read()

        # 添加时间戳
        if timestamp_server:
            signature_params['timestamper'] = timestamp_server

        # 执行签名
        signed_pdf = cms.sign(pdf_data, **signature_params)

        # 写入输出文件
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'wb') as f:
            f.write(signed_pdf)

        print(f"\n签名完成!")
        print(f"  输出文件: {output_file}")
        return True

    except Exception as e:
        print(f"签名失败: {e}")
        return False


def sign_pdf_pkcs12(
    input_file: str,
    output_file: str,
    p12_path: str,
    password: str,
    reason: str = "Document signed",
    location: str = "",
    contact_info: str = "",
    visible: bool = False,
    page: int = 0,
    box: tuple = (0, 0, 0, 0),
    timestamp_server: Optional[str] = None,
    digest_algorithm: str = "sha256",
    verbose: bool = False
) -> bool:
    """
    使用 PKCS#12 文件对 PDF 进行数字签名。

    Args:
        input_file: 输入 PDF 文件路径
        output_file: 输出 PDF 文件路径
        p12_path: PKCS#12 文件路径（.p12 或 .pfx）
        password: PKCS#12 文件密码
        reason: 签名原因
        location: 签名地点
        contact_info: 联系信息
        visible: 是否创建可见签名
        page: 签名页码（0-indexed）
        box: 签名框位置 (x, y, width, height)
        timestamp_server: 时间戳服务器 URL
        digest_algorithm: 摘要算法
        verbose: 详细输出模式

    Returns:
        bool: 签名是否成功
    """
    try:
        # 加载 PKCS#12 文件
        private_key, certificate, chain = load_pkcs12(p12_path, password)

        if verbose:
            print(f"输入文件: {input_file}")
            print(f"PKCS#12 文件: {p12_path}")
            print(f"签名者: {certificate.subject.rfc4514_string()}")
            print(f"签名原因: {reason}")
            print(f"摘要算法: {digest_algorithm}")

        # 读取 PDF 文件
        with open(input_file, 'rb') as f:
            pdf_data = f.read()

        # 构建签名参数
        signature_params = {
            'signature': private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ),
            'certificate': certificate.public_bytes(serialization.Encoding.PEM),
            'reason': reason,
            'location': location,
            'contact': contact_info,
            'signingtime': datetime.utcnow(),
            'algorithm': digest_algorithm,
        }

        # 添加证书链
        if chain:
            signature_params['chain'] = [
                cert.public_bytes(serialization.Encoding.PEM) for cert in chain
            ]

        # 添加可见签名框
        if visible and box != (0, 0, 0, 0):
            signature_params['signaturebox'] = box
            signature_params['signaturepage'] = page

        # 添加时间戳
        if timestamp_server:
            signature_params['timestamper'] = timestamp_server

        # 执行签名
        signed_pdf = cms.sign(pdf_data, **signature_params)

        # 写入输出文件
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'wb') as f:
            f.write(signed_pdf)

        print(f"\n签名完成!")
        print(f"  输出文件: {output_file}")
        return True

    except Exception as e:
        print(f"签名失败: {e}")
        return False


# ============================================================
# 签名验证功能
# ============================================================

def verify_pdf_signature(
    pdf_path: str,
    trusted_certs: Optional[list[str]] = None,
    verbose: bool = False
) -> list[SignatureInfo]:
    """
    验证 PDF 文件的数字签名。

    Args:
        pdf_path: PDF 文件路径
        trusted_certs: 信任的证书路径列表（用于证书链验证）
        verbose: 详细输出模式

    Returns:
        list[SignatureInfo]: 签名信息列表
    """
    from endesive.pdf import verify

    signatures = []

    try:
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()

        if verbose:
            print(f"验证文件: {pdf_path}")

        # 获取签名信息
        results = verify(pdf_data, trusted_certs)

        for result in results:
            info = SignatureInfo()

            # 提取签名者信息
            if 'signer' in result:
                cert = result['signer']
                info.signer_name = cert.subject.rfc4514_string()
                info.serial_number = str(cert.serial_number)
                info.issuer = cert.issuer.rfc4514_string()

            # 提取签名时间
            if 'signing_time' in result:
                info.signing_time = result['signing_time']

            # 提取签名属性
            if 'reason' in result:
                info.reason = result['reason']
            if 'location' in result:
                info.location = result['location']

            # 验证结果
            info.is_valid = result.get('valid', False)
            info.is_trusted = result.get('trusted', False)

            if not info.is_valid:
                info.error_message = result.get('error', 'Unknown error')

            signatures.append(info)

        return signatures

    except Exception as e:
        print(f"验证失败: {e}")
        return signatures


def check_pdf_signed(pdf_path: str) -> bool:
    """
    检查 PDF 文件是否已被签名。

    Args:
        pdf_path: PDF 文件路径

    Returns:
        bool: 是否包含签名
    """
    try:
        from pypdf import PdfReader

        reader = PdfReader(pdf_path)

        # 检查是否有签名域
        if '/AcroForm' in reader.trailer['/Root']:
            form = reader.trailer['/Root']['/AcroForm']
            if '/Fields' in form:
                fields = form['/Fields']
                for field in fields:
                    field_obj = field.get_object()
                    if '/FT' in field_obj and field_obj['/FT'] == '/Sig':
                        return True

        # 检查是否有签名
        if '/Perms' in reader.trailer['/Root']:
            perms = reader.trailer['/Root']['/Perms']
            if '/DocMDP' in perms or '/UR3' in perms:
                return True

        return False

    except Exception:
        return False


# ============================================================
# 签名信息提取功能
# ============================================================

def extract_signature_info(
    pdf_path: str,
    output_format: str = "text",
    verbose: bool = False
) -> list[dict]:
    """
    提取 PDF 文件中的签名信息。

    Args:
        pdf_path: PDF 文件路径
        output_format: 输出格式（text, json）
        verbose: 详细输出模式

    Returns:
        list[dict]: 签名信息字典列表
    """
    from pypdf import PdfReader
    import json

    signatures = []

    try:
        reader = PdfReader(pdf_path)

        if verbose:
            print(f"提取签名信息: {pdf_path}")
            print(f"页数: {len(reader.pages)}")

        # 提取签名域信息
        if '/AcroForm' in reader.trailer['/Root']:
            form = reader.trailer['/Root']['/AcroForm'].get_object()
            if '/Fields' in form:
                fields = form['/Fields']
                for field in fields:
                    field_obj = field.get_object()
                    if '/FT' in field_obj and field_obj['/FT'] == '/Sig':
                        sig_info = {
                            'field_name': field_obj.get('/T', 'Unknown'),
                            'type': 'Signature Field',
                            'value': field_obj.get('/V', {}).get('/Name', ''),
                        }

                        # 提取签名值详情
                        if '/V' in field_obj:
                            sig_value = field_obj['/V'].get_object()
                            sig_info['details'] = {}

                            if '/Name' in sig_value:
                                sig_info['details']['name'] = str(sig_value['/Name'])
                            if '/Reason' in sig_value:
                                sig_info['details']['reason'] = str(sig_value['/Reason'])
                            if '/M' in sig_value:
                                sig_info['details']['date'] = str(sig_value['/M'])
                            if '/Location' in sig_value:
                                sig_info['details']['location'] = str(sig_value['/Location'])
                            if '/ContactInfo' in sig_value:
                                sig_info['details']['contact'] = str(sig_value['/ContactInfo'])

                        signatures.append(sig_info)

        # 输出结果
        if output_format == 'json':
            print(json.dumps(signatures, indent=2, default=str))
        else:
            print(f"\n找到 {len(signatures)} 个签名:")
            for i, sig in enumerate(signatures, 1):
                print(f"\n签名 {i}:")
                print(f"  字段名称: {sig.get('field_name', 'N/A')}")
                print(f"  类型: {sig.get('type', 'N/A')}")
                print(f"  值: {sig.get('value', 'N/A')}")

                details = sig.get('details', {})
                if details:
                    print("  详情:")
                    for key, value in details.items():
                        print(f"    {key}: {value}")

        return signatures

    except Exception as e:
        print(f"提取失败: {e}")
        return []


# ============================================================
# 自签名证书生成（用于测试）
# ============================================================

def generate_self_signed_certificate(
    common_name: str,
    output_cert: str,
    output_key: str,
    key_size: int = 2048,
    days_valid: int = 365,
    country: str = "CN",
    state: str = "Beijing",
    locality: str = "Beijing",
    organization: str = "Test Organization",
    email: str = "",
    password: Optional[str] = None,
    verbose: bool = False
) -> bool:
    """
    生成自签名证书（用于测试目的）。

    警告：自签名证书仅用于测试，不应用于生产环境！

    Args:
        common_name: 通用名称（CN）
        output_cert: 输出证书文件路径
        output_key: 输出私钥文件路径
        key_size: 密钥长度（默认 2048 位）
        days_valid: 有效期（天）
        country: 国家代码
        state: 州/省
        locality: 城市
        organization: 组织名称
        email: 电子邮件
        password: 私钥密码（可选）
        verbose: 详细输出模式

    Returns:
        bool: 是否成功
    """
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import hashes, serialization
        from datetime import datetime, timedelta

        if verbose:
            print(f"生成自签名证书...")
            print(f"  通用名称: {common_name}")
            print(f"  有效期: {days_valid} 天")
            print(f"  密钥长度: {key_size} 位")

        # 生成私钥
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )

        # 构建证书主题
        name_attrs = [
            x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
            x509.NameAttribute(NameOID.LOCALITY_NAME, locality),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ]
        if email:
            name_attrs.append(
                x509.NameAttribute(NameOID.EMAIL_ADDRESS, email)
            )

        subject = issuer = x509.Name(name_attrs)

        # 构建证书
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=days_valid))
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    key_cert_sign=True,
                    crl_sign=True,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .add_extension(
                x509.ExtendedKeyUsage([
                    x509.oid.ExtendedKeyUsageOID.CODE_SIGNING,
                    x509.oid.ExtendedKeyUsageOID.EMAIL_PROTECTION,
                ]),
                critical=False,
            )
            .sign(private_key, hashes.SHA256())
        )

        # 保存证书
        Path(output_cert).parent.mkdir(parents=True, exist_ok=True)
        with open(output_cert, 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        # 保存私钥
        Path(output_key).parent.mkdir(parents=True, exist_ok=True)
        encryption = (
            serialization.BestAvailableEncryption(password.encode())
            if password else serialization.NoEncryption()
        )
        with open(output_key, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption,
            ))

        print(f"\n证书生成成功!")
        print(f"  证书文件: {output_cert}")
        print(f"  私钥文件: {output_key}")
        print(f"\n警告: 自签名证书仅用于测试目的!")

        return True

    except Exception as e:
        print(f"生成证书失败: {e}")
        return False


# ============================================================
# 命令行接口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='PDF 数字签名工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
子命令:
  sign       对 PDF 文件进行数字签名
  verify     验证 PDF 签名
  extract    提取签名信息
  generate   生成自签名证书（用于测试）

示例:
  # 使用证书签名
  %(prog)s sign input.pdf -c cert.pem -k key.pem -o signed.pdf

  # 使用 PKCS#12 文件签名
  %(prog)s sign input.pdf --p12 cert.p12 -p password -o signed.pdf

  # 验证签名
  %(prog)s verify signed.pdf

  # 提取签名信息
  %(prog)s extract signed.pdf --format json

  # 生成测试证书
  %(prog)s generate --cn "Test User" -o cert.pem -k key.pem
'''
    )

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # ---------------------------
    # sign 子命令
    # ---------------------------
    sign_parser = subparsers.add_parser('sign', help='对 PDF 文件进行数字签名')

    sign_parser.add_argument('input', help='输入 PDF 文件')

    sign_parser.add_argument(
        '-o', '--output',
        required=True,
        help='输出 PDF 文件'
    )

    # 证书选项
    cert_group = sign_parser.add_mutually_exclusive_group(required=True)
    cert_group.add_argument(
        '-c', '--cert',
        help='证书文件（PEM 格式）'
    )
    cert_group.add_argument(
        '--p12',
        help='PKCS#12 文件（.p12 或 .pfx）'
    )

    sign_parser.add_argument(
        '-k', '--key',
        help='私钥文件（PEM 格式，与 -c 配合使用）'
    )

    sign_parser.add_argument(
        '-p', '--password',
        help='私钥或 PKCS#12 文件密码'
    )

    sign_parser.add_argument(
        '--reason',
        default='Document signed',
        help='签名原因'
    )

    sign_parser.add_argument(
        '--location',
        default='',
        help='签名地点'
    )

    sign_parser.add_argument(
        '--contact',
        default='',
        help='联系信息'
    )

    sign_parser.add_argument(
        '--visible',
        action='store_true',
        help='创建可见签名'
    )

    sign_parser.add_argument(
        '--page',
        type=int,
        default=0,
        help='签名页码（0-indexed，默认为 0）'
    )

    sign_parser.add_argument(
        '--box',
        type=str,
        default='0,0,0,0',
        help='签名框位置 (x,y,width,height)'
    )

    sign_parser.add_argument(
        '--timestamp',
        help='时间戳服务器 URL'
    )

    sign_parser.add_argument(
        '--algorithm',
        choices=['sha1', 'sha256', 'sha384', 'sha512'],
        default='sha256',
        help='摘要算法（默认 sha256）'
    )

    sign_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='详细输出模式'
    )

    # ---------------------------
    # verify 子命令
    # ---------------------------
    verify_parser = subparsers.add_parser('verify', help='验证 PDF 签名')

    verify_parser.add_argument('input', help='PDF 文件')

    verify_parser.add_argument(
        '--trusted-cert',
        action='append',
        help='信任的证书文件（可多次指定）'
    )

    verify_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='详细输出模式'
    )

    # ---------------------------
    # extract 子命令
    # ---------------------------
    extract_parser = subparsers.add_parser('extract', help='提取签名信息')

    extract_parser.add_argument('input', help='PDF 文件')

    extract_parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='输出格式（默认 text）'
    )

    extract_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='详细输出模式'
    )

    # ---------------------------
    # generate 子命令
    # ---------------------------
    gen_parser = subparsers.add_parser('generate', help='生成自签名证书（仅用于测试）')

    gen_parser.add_argument(
        '--cn',
        required=True,
        help='通用名称（Common Name）'
    )

    gen_parser.add_argument(
        '-o', '--output-cert',
        default='cert.pem',
        help='输出证书文件（默认 cert.pem）'
    )

    gen_parser.add_argument(
        '-k', '--output-key',
        default='key.pem',
        help='输出私钥文件（默认 key.pem）'
    )

    gen_parser.add_argument(
        '--days',
        type=int,
        default=365,
        help='有效期（天，默认 365）'
    )

    gen_parser.add_argument(
        '--key-size',
        type=int,
        default=2048,
        help='密钥长度（默认 2048）'
    )

    gen_parser.add_argument(
        '--country',
        default='CN',
        help='国家代码'
    )

    gen_parser.add_argument(
        '--state',
        default='Beijing',
        help='州/省'
    )

    gen_parser.add_argument(
        '--locality',
        default='Beijing',
        help='城市'
    )

    gen_parser.add_argument(
        '--org',
        default='Test Organization',
        help='组织名称'
    )

    gen_parser.add_argument(
        '--email',
        default='',
        help='电子邮件'
    )

    gen_parser.add_argument(
        '-p', '--password',
        help='私钥密码'
    )

    gen_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='详细输出模式'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 执行命令
    if args.command == 'sign':
        # 检查输入文件
        if not Path(args.input).exists():
            print(f"错误: 文件不存在 - {args.input}")
            sys.exit(1)

        # 解析签名框
        box = tuple(map(int, args.box.split(',')))

        if args.p12:
            # 使用 PKCS#12 文件签名
            success = sign_pdf_pkcs12(
                input_file=args.input,
                output_file=args.output,
                p12_path=args.p12,
                password=args.password or '',
                reason=args.reason,
                location=args.location,
                contact_info=args.contact,
                visible=args.visible,
                page=args.page,
                box=box,
                timestamp_server=args.timestamp,
                digest_algorithm=args.algorithm,
                verbose=args.verbose
            )
        else:
            # 使用 PEM 证书签名
            if not args.key:
                print("错误: 使用 PEM 证书时需要指定私钥文件 (-k)")
                sys.exit(1)

            success = sign_pdf(
                input_file=args.input,
                output_file=args.output,
                cert_path=args.cert,
                key_path=args.key,
                key_password=args.password,
                reason=args.reason,
                location=args.location,
                contact_info=args.contact,
                visible=args.visible,
                page=args.page,
                box=box,
                timestamp_server=args.timestamp,
                digest_algorithm=args.algorithm,
                verbose=args.verbose
            )

        sys.exit(0 if success else 1)

    elif args.command == 'verify':
        if not Path(args.input).exists():
            print(f"错误: 文件不存在 - {args.input}")
            sys.exit(1)

        trusted_certs = args.trusted_cert if args.trusted_cert else None
        signatures = verify_pdf_signature(
            args.input,
            trusted_certs=trusted_certs,
            verbose=args.verbose
        )

        print(f"\n找到 {len(signatures)} 个签名:")
        for i, sig in enumerate(signatures, 1):
            print(f"\n签名 {i}:")
            print(f"  签名者: {sig.signer_name}")
            print(f"  时间: {sig.signing_time}")
            print(f"  原因: {sig.reason}")
            print(f"  地点: {sig.location}")
            print(f"  有效: {'是' if sig.is_valid else '否'}")
            print(f"  受信任: {'是' if sig.is_trusted else '否'}")
            if sig.error_message:
                print(f"  错误: {sig.error_message}")

        # 返回码：如果有任何无效签名则返回 1
        all_valid = all(sig.is_valid for sig in signatures)
        sys.exit(0 if all_valid or not signatures else 1)

    elif args.command == 'extract':
        if not Path(args.input).exists():
            print(f"错误: 文件不存在 - {args.input}")
            sys.exit(1)

        extract_signature_info(
            args.input,
            output_format=args.format,
            verbose=args.verbose
        )

    elif args.command == 'generate':
        success = generate_self_signed_certificate(
            common_name=args.cn,
            output_cert=args.output_cert,
            output_key=args.output_key,
            key_size=args.key_size,
            days_valid=args.days,
            country=args.country,
            state=args.state,
            locality=args.locality,
            organization=args.org,
            email=args.email,
            password=args.password,
            verbose=args.verbose
        )
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
