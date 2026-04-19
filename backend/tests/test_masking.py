"""Tests for dwyeapi.masking."""

from dwyeapi.masking import (
    mask_address,
    mask_bank_card,
    mask_email,
    mask_id_card,
    mask_ip,
    mask_license_plate,
    mask_name,
    mask_phone,
    mask_text,
)


class TestMaskPhone:
    def test_standard_phone(self):
        assert mask_phone("13812345678") == "138****5678"

    def test_another_phone(self):
        assert mask_phone("15099998888") == "150****8888"

    def test_empty_string(self):
        assert mask_phone("") == ""

    def test_too_short(self):
        assert mask_phone("1381234") == "1381234"

    def test_too_long(self):
        assert mask_phone("138123456789") == "138123456789"

    def test_non_digit(self):
        assert mask_phone("abcdefghijk") == "abcdefghijk"

    def test_with_country_code(self):
        assert mask_phone("+8613812345678") == "+8613812345678"


class TestMaskEmail:
    def test_standard_email(self):
        assert mask_email("zhangsan@gmail.com") == "z***@gmail.com"

    def test_single_char_local(self):
        assert mask_email("a@example.com") == "a***@example.com"

    def test_empty_string(self):
        assert mask_email("") == ""

    def test_no_at_sign(self):
        assert mask_email("invalidemail") == "invalidemail"

    def test_multiple_at_signs(self):
        assert mask_email("a@b@c.com") == "a@b@c.com"

    def test_short_local_part(self):
        assert mask_email("ab@qq.com") == "a***@qq.com"


class TestMaskIdCard:
    def test_standard_18_digit(self):
        assert mask_id_card("420123199001011234") == "420***********1234"

    def test_18_digit_with_x(self):
        assert mask_id_card("42012319900101123X") == "420***********123X"

    def test_empty_string(self):
        assert mask_id_card("") == ""

    def test_wrong_length(self):
        assert mask_id_card("42012319900101") == "42012319900101"

    def test_non_id_card(self):
        assert mask_id_card("abcdefghijklmnopqr") == "abcdefghijklmnopqr"


class TestMaskBankCard:
    def test_16_digit_card(self):
        assert mask_bank_card("6222021234561234") == "6222********1234"

    def test_19_digit_card(self):
        assert mask_bank_card("6222021234567891234") == "6222***********1234"

    def test_empty_string(self):
        assert mask_bank_card("") == ""

    def test_too_short(self):
        assert mask_bank_card("1234567") == "1234567"

    def test_non_digit(self):
        assert mask_bank_card("abcdefghijklmnop") == "abcdefghijklmnop"


class TestMaskName:
    def test_two_char_name(self):
        assert mask_name("张三") == "张*"

    def test_three_char_name(self):
        assert mask_name("张三明") == "张*明"

    def test_four_char_name(self):
        assert mask_name("欧阳三明") == "欧**明"

    def test_single_char_name(self):
        assert mask_name("张") == "张"

    def test_empty_string(self):
        assert mask_name("") == ""

    def test_english_two_char(self):
        assert mask_name("AB") == "A*"

    def test_english_long_name(self):
        assert mask_name("Alice") == "A***e"


class TestMaskAddress:
    def test_full_address(self):
        assert mask_address("浙江省杭州市西湖区文三路100号") == "浙江省杭州市西湖区****"

    def test_province_city(self):
        assert mask_address("广东省深圳市南山区科技园") == "广东省深圳市南山区****"

    def test_municipality(self):
        assert mask_address("北京市朝阳区望京街道123号") == "北京市朝阳区****"

    def test_autonomous_region(self):
        assert mask_address("内蒙古自治区呼和浩特市赛罕区大学路") == "内蒙古自治区呼和浩特市赛罕区****"

    def test_with_town(self):
        assert mask_address("浙江省杭州市余杭区仓前镇文一西路") == "浙江省杭州市余杭区仓前镇****"

    def test_no_match_long(self):
        assert mask_address("某个不匹配的长地址信息内容") == "某个不匹配的****"

    def test_no_match_short(self):
        assert mask_address("短地址") == "短地址"

    def test_empty_string(self):
        assert mask_address("") == ""

    def test_county(self):
        assert mask_address("河南省信阳市光山县紫水大道") == "河南省信阳市光山县****"


class TestMaskIp:
    def test_standard_ipv4(self):
        assert mask_ip("192.168.1.100") == "192.168.1.*"

    def test_simple_ip(self):
        assert mask_ip("10.0.0.1") == "10.0.0.*"

    def test_empty_string(self):
        assert mask_ip("") == ""

    def test_not_ip(self):
        assert mask_ip("not-an-ip") == "not-an-ip"

    def test_ipv6(self):
        assert mask_ip("::1") == "::1"

    def test_incomplete_ip(self):
        assert mask_ip("192.168.1") == "192.168.1"


class TestMaskLicensePlate:
    def test_standard_plate(self):
        assert mask_license_plate("浙A12345") == "浙A***5"

    def test_new_energy_plate(self):
        assert mask_license_plate("浙AD12345") == "浙A***5"

    def test_another_plate(self):
        assert mask_license_plate("京B88888") == "京B***8"

    def test_empty_string(self):
        assert mask_license_plate("") == ""

    def test_too_short(self):
        assert mask_license_plate("浙A") == "浙A"

    def test_non_plate(self):
        assert mask_license_plate("abc") == "abc"


class TestMaskText:
    def test_default_params(self):
        assert mask_text("abcdef") == "a****f"

    def test_custom_start_end(self):
        assert mask_text("1234567890", start=2, end=3) == "12*****890"

    def test_custom_mask_char(self):
        assert mask_text("abcdef", mask_char="#") == "a####f"

    def test_empty_string(self):
        assert mask_text("") == ""

    def test_single_char(self):
        assert mask_text("a") == "a"

    def test_two_chars_default(self):
        assert mask_text("ab") == "ab"

    def test_start_end_exceed_length(self):
        assert mask_text("abc", start=5, end=5) == "abc"

    def test_start_end_equal_length(self):
        assert mask_text("abc", start=2, end=1) == "abc"

    def test_zero_start(self):
        assert mask_text("abcdef", start=0, end=1) == "*****f"

    def test_zero_end(self):
        assert mask_text("abcdef", start=1, end=0) == "a*****"
