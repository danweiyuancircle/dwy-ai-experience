import { describe, it, expect } from 'vitest'
import {
  maskPhone,
  maskEmail,
  maskIdCard,
  maskBankCard,
  maskName,
  maskAddress,
  maskIp,
  maskLicensePlate,
  maskText,
} from '@/masking'

describe('maskPhone', () => {
  it('标准11位手机号', () => {
    expect(maskPhone('13812345678')).toBe('138****5678')
  })

  it('空字符串原样返回', () => {
    expect(maskPhone('')).toBe('')
  })

  it('格式不匹配原样返回（位数不对）', () => {
    expect(maskPhone('1381234')).toBe('1381234')
  })

  it('格式不匹配原样返回（非数字）', () => {
    expect(maskPhone('abcdefghijk')).toBe('abcdefghijk')
  })

  it('不同号段手机号', () => {
    expect(maskPhone('15999998888')).toBe('159****8888')
    expect(maskPhone('18600001111')).toBe('186****1111')
  })
})

describe('maskEmail', () => {
  it('标准邮箱', () => {
    expect(maskEmail('zhangsan@gmail.com')).toBe('z***@gmail.com')
  })

  it('空字符串原样返回', () => {
    expect(maskEmail('')).toBe('')
  })

  it('无@符号原样返回', () => {
    expect(maskEmail('notanemail')).toBe('notanemail')
  })

  it('单字符用户名', () => {
    expect(maskEmail('a@example.com')).toBe('a***@example.com')
  })

  it('多字符用户名只保留首字符', () => {
    expect(maskEmail('longusername@qq.com')).toBe('l***@qq.com')
  })

  it('多个@符号原样返回', () => {
    expect(maskEmail('a@b@c.com')).toBe('a@b@c.com')
  })
})

describe('maskIdCard', () => {
  it('18位身份证', () => {
    expect(maskIdCard('420106199901011234')).toBe('420***********1234')
  })

  it('空字符串原样返回', () => {
    expect(maskIdCard('')).toBe('')
  })

  it('格式不匹配原样返回', () => {
    expect(maskIdCard('12345')).toBe('12345')
  })

  it('15位身份证原样返回（仅支持18位）', () => {
    expect(maskIdCard('420106990101123')).toBe('420106990101123')
  })

  it('18位末尾X的身份证', () => {
    expect(maskIdCard('42010619990101123X')).toBe('420***********123X')
  })
})

describe('maskBankCard', () => {
  it('16位银行卡', () => {
    expect(maskBankCard('6222021234561234')).toBe('6222********1234')
  })

  it('19位银行卡', () => {
    expect(maskBankCard('6222021234561234567')).toBe('6222***********4567')
  })

  it('空字符串原样返回', () => {
    expect(maskBankCard('')).toBe('')
  })

  it('格式不匹配原样返回（位数太短）', () => {
    expect(maskBankCard('1234')).toBe('1234')
  })

  it('格式不匹配原样返回（非数字）', () => {
    expect(maskBankCard('abcdefghijklmnop')).toBe('abcdefghijklmnop')
  })
})

describe('maskName', () => {
  it('2字姓名', () => {
    expect(maskName('张三')).toBe('张*')
  })

  it('3字姓名', () => {
    expect(maskName('张三明')).toBe('张*明')
  })

  it('4字姓名', () => {
    expect(maskName('欧阳三明')).toBe('欧**明')
  })

  it('空字符串原样返回', () => {
    expect(maskName('')).toBe('')
  })

  it('单字原样返回', () => {
    expect(maskName('张')).toBe('张')
  })
})

describe('maskAddress', () => {
  it('匹配省市区', () => {
    expect(maskAddress('浙江省杭州市西湖区文三路100号')).toBe('浙江省杭州市西湖区****')
  })

  it('匹配省市', () => {
    expect(maskAddress('广东省深圳市南山大道1号')).toBe('广东省深圳市****')
  })

  it('匹配自治区', () => {
    expect(maskAddress('广西壮族自治区南宁市青秀区某路')).toBe('广西壮族自治区南宁市青秀区****')
  })

  it('匹配市辖区（直辖市）', () => {
    expect(maskAddress('北京市朝阳区建国路88号')).toBe('北京市朝阳区****')
  })

  it('不匹配行政区划，保留前6字符', () => {
    expect(maskAddress('某个不知名的详细地址信息')).toBe('某个不知名的****')
  })

  it('空字符串原样返回', () => {
    expect(maskAddress('')).toBe('')
  })

  it('不足6字符原样返回', () => {
    expect(maskAddress('短地址')).toBe('短地址')
  })
})

describe('maskIp', () => {
  it('标准IPv4', () => {
    expect(maskIp('192.168.1.100')).toBe('192.168.1.*')
  })

  it('空字符串原样返回', () => {
    expect(maskIp('')).toBe('')
  })

  it('格式不匹配原样返回', () => {
    expect(maskIp('not-an-ip')).toBe('not-an-ip')
  })

  it('只有3段原样返回', () => {
    expect(maskIp('192.168.1')).toBe('192.168.1')
  })
})

describe('maskLicensePlate', () => {
  it('标准车牌（7位）', () => {
    expect(maskLicensePlate('浙A12348')).toBe('浙A***8')
  })

  it('新能源车牌（8位）', () => {
    expect(maskLicensePlate('浙AD12348')).toBe('浙A***8')
  })

  it('空字符串原样返回', () => {
    expect(maskLicensePlate('')).toBe('')
  })

  it('格式不匹配原样返回', () => {
    expect(maskLicensePlate('AB')).toBe('AB')
  })
})

describe('maskText', () => {
  it('默认保留首尾各1位', () => {
    expect(maskText('hello')).toBe('h***o')
  })

  it('自定义保留首尾位数', () => {
    expect(maskText('1234567890', 2, 3)).toBe('12*****890')
  })

  it('自定义脱敏字符', () => {
    expect(maskText('hello', 1, 1, '#')).toBe('h###o')
  })

  it('空字符串原样返回', () => {
    expect(maskText('')).toBe('')
  })

  it('长度不足保留位数时原样返回', () => {
    expect(maskText('ab', 1, 1)).toBe('ab')
  })

  it('start + end 等于字符串长度时原样返回', () => {
    expect(maskText('ab', 1, 1)).toBe('ab')
  })

  it('start=0 时不保留头部', () => {
    expect(maskText('hello', 0, 1)).toBe('****o')
  })

  it('end=0 时不保留尾部', () => {
    expect(maskText('hello', 1, 0)).toBe('h****')
  })
})
