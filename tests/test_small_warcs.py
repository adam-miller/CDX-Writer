#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import py
import os
import sys

# {warc-filename: output-of-cdx_writer.py--all-records, ...}
warcs_all_records = {
     #from IMF NLI ingest 2018-08
    # '10_digit_date.arc.gz': [
    #     b'filedesc://IM_NLI_fb-20160209153640-00005-ext.arc 20160209153640 filedesc://IM_NLI_fb-20160209153640-00005-ext.arc warc/filedesc - PSBTZHIJYAY6LJM4WFI2NCA7X6OQ3FMF - - 666 0 10_digit_date.arc.gz',
    #     b'com,facebook)/vanishing-ireland-110498185666457 20160209000000 https://www.facebook.com/Vanishing-Ireland-110498185666457/ text/html 200 2QHUP2CGE5UURBV5YBDCEQR6SHQ3MSOW - - 71299 666 10_digit_date.arc.gz'
    # ],
     #from IMF ingest 2018-08
    # '14_digit_plus_text_date.arc.gz': [
    #     b'filedesc://IM_NLI_test_fb-20160211113933-00417-ext.arc 20160211113933 filedesc://IM_NLI_test_fb-20160211113933-00417-ext.arc warc/filedesc - O5XJHHCGP7QZESK2PGLRJWGLCLLXVQHA - - 659 0 14_digit_plus_text_date.arc.gz',
    #     b'net,fbcdn,xx,scontent-cdg2-1)/300261_10150266886136400_4821326_n. 20160211000000 https://scontent-cdg2-1.xx.fbcdn.net/300261_10150266886136400_4821326_n. text/html 200 ZRNNAI6EJ7HCNZWNB4ZNHQSXBWTEXZQ7 - - 1072 659 14_digit_plus_text_date.arc.gz'
    # ],
    #from IMF UNESCO ingest 2018-08
    # '15_digit_date.arc.gz': [
    #     b'filedesc://IM_UNESCO_122015-twitter.com_unesco_fr-20160113115026-00001-ext.arc 20160113115026 filedesc://IM_UNESCO_122015-twitter.com_unesco_fr-20160113115026-00001-ext.arc warc/filedesc - HPFTNFJ64ZUZW4RFTNEIVLUK2NRGX6NN - - 673 0 15_digit_date.arc.gz',
    #     b'com,twitter)/unesco_fr.xml 20151200000000 http://twitter.com/unesco_fr.xml text/xml 200 Q6TYZPCHPZEMHLLIXWNW6MBBCGAJV3MR - - 723272 673 15_digit_date.arc.gz'
    # ],
    #from INA-HISTORICAL-1996-GROUP-AAA-20100812000000-00000-c/INA-HISTORICAL-2000-GROUP-ACS-20100812000000-00001.arc.gz
    # has two padding '\n's. 3.x had incorrect digest FL5ZDSVRACUUD2GUCKOWWY6LPPLR7TSJ (included extra '\n' at the end) for response record
    '16_digit_date.arc.gz': [
        b'filedesc://INA-HISTORICAL-2000-GROUP-ACS-20100812000000-00001.arc 20100812000000 filedesc://INA-HISTORICAL-2000-GROUP-ACS-20100812000000-00001.arc warc/filedesc - VXEDWGPHSNERWHDOUD6YWRWNT4ZOLEX4 - - 168 0 16_digit_date.arc.gz',
        b'com,afp)/home/img/es.gif 20000823054100 http://www.afp.com:80/home/img/es.gif image/gif 200 TUQLSV5PWCWHL2X3O67JULYLMWXGA252 - - 936 168 16_digit_date.arc.gz'
    ],
    #from IMG_XAB_001010144441-c/IMG_XBB_000918161534.arc.gz
    # '18_digit_date.arc.gz': [
    #     b'filedesc:///ia/crawl1/md1/2000-09-18-13-36-crawl/IMG_XBB_000918161534.arc 20000918231534 filedesc:///ia/crawl1/md1/2000-09-18-13-36-crawl/IMG_XBB_000918161534.arc warc/filedesc - VXEDWGPHSNERWHDOUD6YWRWNT4ZOLEX4 - - 181 0 18_digit_date.arc.gz',
    #     b'com,spaceports,mars)/~jddp/images/links_off.gif 20000918002300 http://mars.spaceports.com:80/~jddp/images/links_off.gif image/gif 200 V7FZGUGSTVX4EKWAT46CTBB47KSIYO7F - - 1165 181 18_digit_date.arc.gz'
    # ],
    # from ARCHIVEIT-7855-TEST-JOB270756-SEED1365208-20170303022116385-00000-qh0i1erc.warc.gz
    '304-response.warc.gz': [
        b'gov,nasa,kepler)/layout/mws/main.css 20170303024245 https://kepler.nasa.gov/layout/mws/main.css unk 304 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 630 0 304-response.warc.gz'
    ],
    '304-revisit.warc.gz': [
        b'org,wikipedia)/ 20170329205748 https://www.wikipedia.org/ warc/revisit - LC43NA4MJILWX5KPDVBVIRD2OMPTNLJD - - 356 0 304-revisit.warc.gz'
    ],
    #from INA-HISTORICAL-1996-GROUP-AAA-20100812000000-00000-c/INA-HISTORICAL-2000-GROUP-ACS-20100812000000-00001.arc.gz, fixed in warctools changeset 92:ca95fa09848b
    # 'alexa_charset_in_header.arc.gz': [
    #     b'filedesc://INA-HISTORICAL-2000-GROUP-ACS-20100812000000-00001.arc 20100812000000 filedesc://INA-HISTORICAL-2000-GROUP-ACS-20100812000000-00001.arc warc/filedesc - VXEDWGPHSNERWHDOUD6YWRWNT4ZOLEX4 - - 168 0 alexa_charset_in_header.arc.gz',
    #     b'fr,allocine,free)/tv/cineaction.asp 20000824015105 http://free.allocine.fr:80/tv/cineaction.asp text/html 200 YSO3GBFJ7KRO3OPF7J43J4NMM4LVR7ZY - - 3974 168 alexa_charset_in_header.arc.gz'
    # ],
    'alexa_short_header.arc.gz': [
        b'filedesc://51_23_20110804181044_crawl101.arc.gz 20110804181044 filedesc://51_23_20110804181044_crawl101.arc.gz warc/filedesc - 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 161 0 alexa_short_header.arc.gz',
        b'net,killerjo)/robots.txt 20110804181142 http://www.killerjo.net:80/robots.txt unk 200 YZI2NMZ5ILYICUL3PNYVYQR3KI2YY5EH - - 139 161 alexa_short_header.arc.gz'
    ],
    #from crc24-7-aa-960915931-c/crc24.20001110112006.arc.gz
    'arc_v1_with_v2_header.arc.gz': [
        b'filedesc://crc24.20001110112006.arc 20001110112000 filedesc://crc24.20001110112006.arc warc/filedesc - VXEDWGPHSNERWHDOUD6YWRWNT4ZOLEX4 - - 179 0 arc_v1_with_v2_header.arc.gz',
        b'com,cdnow)/cgi-bin/mserver/pagename=/rp/cdn/find/discography.html/artistid=henderson*joe/select=music 20001110112000 http://www.cdnow.com:80/cgi-bin/mserver/pagename=/RP/CDN/FIND/discography.html/artistid=HENDERSON*JOE/select=music text/html 200 Z7XLU7KXZVH3AAC6ZZLMMRVWPHC44ALO - - 8884 179 arc_v1_with_v2_header.arc.gz'
    ],
    # moved to test_fields.py
    # 'bad_mime_type.arc.gz': [
    #     b'filedesc://live-20120407151931218-00299.arc 20120407151931 filedesc://live-20120407151931218-00299.arc warc/filedesc - VXEDWGPHSNERWHDOUD6YWRWNT4ZOLEX4 - - 153 0 bad_mime_type.arc.gz',
    #     b'net,naver,cafethumb)/20101223_84/qkrgns3_129303386816936xuq_jpg/imag0030_qkrgns3.jpg 20120407152447 http://cafethumb.naver.net/20101223_84/qkrgns3_129303386816936xUq_jpg/imag0030_qkrgns3.jpg unk 200 OUK52MTLKPEA6STHTFFPFI2JP7G4QBUZ - - 3587 153 bad_mime_type.arc.gz'
    # ],
    # from 1213886081714_1-c/1213886929852_11.arc.gz, contains unicode replacement char. has "Transfer-Encoding:chunked" but response body is not chunk-encoded
    'bad_unicode_host.arc.gz': [
        b'filedesc://1213886929852_11.arc.gz 20080619074849 filedesc://1213886929852_11.arc.gz warc/filedesc - VXEDWGPHSNERWHDOUD6YWRWNT4ZOLEX4 - - 158 0 bad_unicode_host.arc.gz',
        b'net,82,t%ef%bf%bd%04)/ 20080509130938 http://www.t%EF%BF%BD%04.82.net/ text/html 200 V6CPFAFQFDRK2BWCGRXEZYKAGOUMWYM5 - - 416 158 bad_unicode_host.arc.gz'
    ],
    #from wb_urls.ia331232.20070721072555-c/wb_urls.ia331232.us.archive.org.20071008072146.arc.gz
    'bad_url_with_colon_1.arc.gz': [
        b"http://JavaScript:Wtop('www.pick2hand.com/index2.html') 20071008060921 http://JavaScript:Wtop('www.pick2hand.com/index2.html') text/html 200 DANDEM27HUMJBSIAEPFZR5BB2LMNXROO - - 528 0 bad_url_with_colon_1.arc.gz"
    ],
    #from wb_urls.ia331234.20071009100539-c/wb_urls.ia331234.us.archive.org.20071121182609.arc.gz
    'bad_url_with_colon_2.arc.gz': [
        b'http://mhtml:d.hatena.ne.jp/images/top/greenpower_logo.gif 20071121164820 http://mhtml:d.hatena.ne.jp/images/top/greenpower_logo.gif text/html 200 2RFE734TL4XU6RQQOSM2BVPRGS5KGJTS - - 14465 0 bad_url_with_colon_2.arc.gz'
    ],
    #from wb_urls.ia331237.20070519034408-c/wb_urls.ia331237.20070519044148.arc.gz
    'carriage_return_in_url.arc.gz': [
        b'filedesc:///var/tmp/wayback/export/wb_urls.ia331237.20070519044148 20070519044148 filedesc:///var/tmp/wayback/export/wb_urls.ia331237.20070519044148 warc/filedesc - 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 171 0 carriage_return_in_url.arc.gz',
        b'org,cheapchicks)/cgi-bin/count/slcnt.cgi?c=3 20070216134117 http://cheapchicks.org/cgi-bin/count/slcnt.cgi?c=3 text/html 200 DRN2R2KFMNP6SQ6MYXFGSW366YL2IDOA - - 666 171 carriage_return_in_url.arc.gz'
    ],
    #from DX_crawl29.20040711143227-c/DX_crawl29.20040711214146.arc.gz
    'chardet_failure_url.arc.gz': [
        b'filedesc://DX_crawl29.20040711214146.arc 20040711214146 filedesc://DX_crawl29.20040711214146.arc warc/filedesc - 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 153 0 chardet_failure_url.arc.gz',
        b'cn,com,pconline,guide)/gamecomment/post.jsp?column=netgame&topic=%ce%d2%c3%c7%d7%f6%d6%f7%b5%c4%ca%c0%b4%fa%b5%bd%c0%b4%c1%cb%a3%a1%a1%b6%c8%d9%d2%ab%a1%b7%b7%a8%b5%e4%d5q%c9%fa%a3%a1 20040711214255 http://guide.pconline.com.cn:80/gamecomment/post.jsp?column=netgame&topic=\xce\xd2\xc3\xc7\xd7\xf6\xd6\xf7\xb5\xc4\xca\xc0\xb4\xfa\xb5\xbd\xc0\xb4\xc1\xcb\xa3\xa1\xa1\xb6\xc8\xd9\xd2\xab\xa1\xb7\xb7\xa8\xb5\xe4\xd5Q\xc9\xfa\xa3\xa1 text/html 400 YVY3QUSAB6EOL5HYRV3CNKRMZZ6U6K2E - - 485 153 chardet_failure_url.arc.gz'
    ],
    'crlf_at_1k_boundary.warc.gz': [
        b'nz,co,tradeaboat,whitiangamarine)/emailafriend.aspx?item=h4siagw4x00a/wfwao/9gaxg6utmkolwv1zy9nohybsaoj36okttm/cdglv9et4wgw8ywbkoacccfsjvdmf7bge+ke8edgs5h4ib0rue96yj2/r5lixmy1sueue5iihmyms9jl9femizgo6yaew0fx+snckd5d+ow5216i0sj9yb0pzj/i/3z3mannav042wjyfyugogpn6yv2wzgueerk5fqi+msasd88rtsytzkszuc/mtpdowhevxiy3n2+r1n6q9utfvekuy5bonzpqy7blk93yj9dnviit0zjmshgotxc0nuywionfpixfogmm8y6i3rfxxqxd5p95qmiogdi1rvpgkcav+go4nz4r/caicl697pcwfkcqyfw5zts74+snrdessbdz2quceotydcw2gh3hogkrrupiqn9hfdvsb2p3hxp/ygkh9w6+d8jp7tylmalvnjjevst/6wlbqrhwrsnlpxntjxqzrtw7z8e/+o5bfsb6hgwfxzulqz2rnnfvazomgkckthoprtba6cp5ifb8j8sfov7pvwifngclbr28ekmjaebqrznblb4njweisomyenibp/qlvpv4sqarzduhs1qri9toq/toiasrlkpq+sdsbuzqjxij9b/tjgx8biqe129tdob0bdhtexwqq1aoaasxmtqddrykqcrvckjfh1ayszhyl9p6xs6lwmalo2mygxnzegkrvpfr5c/edjp6hr/28egr4fdxyyrwaumhoprqgxyjtq7nqwv7m8jyyvxcfgpx6kz6ftu4nmbahpuhgxd/eddp5y3duicjbcaymmvvmojqxmxb8cpsytv9zcu1rn5ehrp2iypudy+6ihhacaaa= 20110218233256 http://whitiangamarine.tradeaboat.co.nz/emailAFriend.aspx?item=H4sIAGW4X00A%2fwFwAo%2f9gaXg6UTMkoLWV1Zy9nOhybsaOj36okTTM%2fCdGlV9et4wGW8ywbKoacCcFSjvDmf7BgE%2bke8eDGs5H4ib0RuE96Yj2%2fR5LIXmy1SUEue5IiHmYmS9jl9femiZGo6yAeW0fX%2bSnCkd5D%2bOW5216i0SJ9yb0PZJ%2fI%2f3z3manNAv042wJYFyUgOGpN6yV2wZGUEERk5FQI%2bmSASd88RTsytzksZuC%2fmTpDowhevXiY3N2%2br1n6Q9utfvEKuy5bonZPqy7BlK93yJ9DnviiT0ZJMsHGOTXC0NUywIonFpIXfogmm8y6I3RfXxQXD5p95qmiogdI1rvPgKCaV%2bgO4nZ4r%2fCAicl697pcwFKCQyFW5ZTS74%2bSnrdEssBdz2quceotYDcW2GH3hogkrRupiqN9hFdVsb2p3HXP%2fYGkH9W6%2bD8jp7TyLmALvnJJevST%2f6wlbQRhWrsNlPXnTjxQZrTw7z8E%2f%2bo5BFsb6HgWfXzULQZ2RnNFvAZOMgkcKtHopRTbA6cp5ifB8j8sFoV7PVwifNgcLBR28EKMjAeBqRZnBlB4nJwEISomyeNIBP%2fQlvpV4sqArZdUhs1qRi9TOQ%2fToiaSrlKpq%2bSdSbuZqjXIJ9b%2ftjgx8biQe129TDOB0BDHtEXwqq1aoaASxmTqddrYKqCRvcKjfH1aYSZHyL9p6xS6LwMAlO2myGxnZeGkrVpfr5C%2fEDJp6HR%2f28EgR4fdXyyRWauMhoPrQgXYJTq7NQwv7m8JYyvxCfGpX6Kz6ftu4NMBAHPuhGxd%2fEDDP5y3DUIcJBCAyMMvvMOJQXMXb8cpsyTv9ZcU1RN5ehrp2iyPudY%2b6iHHACAAA%3d text/html 200 M4VJCCJQJKPACSSSBHURM572HSDQHO2P - - 2588 0 crlf_at_1k_boundary.warc.gz'
    ],
    #from NLA-AU-CRAWL-006-20120421051259635-00205-02593-crawling119/NLA-AU-CRAWL-006-20120422094450650-02571-3266~web-crawl001.us.archive.org~8443.warc.gz offset 90441596
    'crlf_at_1k_boundary_2.warc.gz': [
        b'au,com,grandtourer)/aspx/login.aspx?4=h6vklmshqnbpvsscb7x7iu2/luokwckr5nsukefi3ygag1wtqor9vtiwv+anh9su4shtqmrrjy53dhqpxif+vjqkb+tajvfhn/sn1oqgaxly4i1ciwbi6jbk+i0fqqn44wt18szrgn95ygnruk9baymdquzchh7i/pak180zcfccrud+lqmmukvlvg0qoq6kvbos8dqo3mh5unwoclxiid2+mbma2rfp/015+o5+dnrq/umof3aettvsy7i/bcmgkbn/6wqknr04kfi4ppwjig2vcw4av8hj2fqbo+3jutdryfgyulizuqjebrh0lmah9sgkrpomwa0hgzmvf1ahoyqbvnbwujeekckxrydnd+dtxyozqlpygn/gcedbkoubmmmldsl+stl4qzomxngk3xnxiw+/csq/pwyimcbtdl/fxvnj6j4l3m5v66mjhxmyzk/wfp7spfzeghl+x4ih9dzzl8nqr/+ma7e6jhmyx4/dwkresqh3mzmiqddmdp6cjtnxapulfamv/tdy1vgjdl4pbiasartibf4nnxlglpvcy+cm3j83nybyytxbrx9+x1vcvnvpo8sipspuyp8xi0glnsmaw/u+owll28euzdlvanmz2j0rcdhtqkyejfhn/rm4z1gkhwn2rexkykbgtnuppthr08v6sur9kagw9dzdyut0go9fjshgpbmnm0uaujtzkshhi0uriz2cnn+arsppeayooy3yedrv7vklewh6mj3yjqfzwj4tbq75wecrm9gw4p+7uwal4wc92gjdip7g1p2cm4vbtvahp1ntq+shd4oot5r6hza2igo85st3ftgfvfj7eolin+dixrjdwa== 20120422095915 https://www.grandtourer.com.au/Aspx/Login.aspx?4=H6VKLMsHqnBpvsscB7x7Iu2%2fLUOKwCKr5nsukefI3ygAG1WTqOR9vtiWv%2banh9sU4sHTQmRRJY53DHQpXiF%2bVjqKB%2btaJvfHn%2fSN1OQgaxlY4i1Ciwbi6jbK%2bI0fQqn44Wt18szRgN95ygNRUK9BaYMdqUzChH7I%2fpAk180zCFCCRUD%2bLqMMuKvLVg0qOQ6Kvbos8DqO3MH5UnwOcLxiID2%2bmBMA2Rfp%2f015%2bo5%2bDNRq%2fUMOF3aETtvSY7i%2fbCmGKBn%2f6WqkNr04Kfi4PPWJIg2VCw4AV8hj2FqbO%2b3JUtdRYfGYulizuQJEbrh0LMah9sGKRPomWA0hgZmvf1AHoYqbVNbwUJeEKCKxrYdND%2bDtxyOzQlpygN%2fgCeDbKOuBMMMLdSl%2bsTl4qZoMXnGK3XNxiw%2b%2fcsq%2fPWyIMCBtdl%2ffXvnJ6J4L3M5v66mjhXmyZk%2fwfp7SpfzegHL%2bX4iH9DZzl8nqr%2f%2bmA7E6JHmyX4%2fDWKrEsqH3MZMIqddmDp6cJtnxAPULfAmv%2fTDY1VGJdl4PBIASArTIBF4nnXLglpvcy%2bcm3j83nyByyTxbRX9%2bX1VcVNvPo8SIpSpuYP8xi0GlNsMaW%2fu%2bowll28EUzDLVAnMz2j0rcdhTqKYEJfhN%2frm4Z1gKhwn2REXKykBGTnupPtHR08V6Sur9kAgW9DZdyUt0Go9fJshGPBmNm0uAUjtzkshhI0UrIz2cnn%2bArspPeaYOOY3YEdrV7VKlEWh6Mj3yjQFZwj4TbQ75WECrM9Gw4p%2b7uWaL4wc92gjDiP7G1P2cM4vBTVAHP1nTQ%2bShD4OoT5r6hZA2igo85St3ftgfvfJ7eOLin%2bdixRJdwA%3d%3d text/html 200 5STDGW7HDWZQ4TPS4GPBOL3TEG7NQRHE - - 6934 0 crlf_at_1k_boundary_2.warc.gz'
    ],
    # 'date_resolution_microsecond.warc.gz': [
    #     b'gov,fcc)/ecfs/search/filings?date_disseminated=[gte]1992-01-09[lte]1992-01-09&limit=100&sort=date_disseminated,desc 20191118125603 https://www.fcc.gov/ecfs/search/filings?date_disseminated=%5Bgte%5D1992-01-09%5Blte%5D1992-01-09&limit=100&sort=date_disseminated,DESC warc/request - I5OL3NNFS3IQMIR7WBSTBCQSWGODBTOT - - 551 0 date_resolution_microsecond.warc.gz'
    # ],
    # 'date_resolution_nanosecond.warc.gz': [
    #     b'gov,fcc)/ecfs/search/filings?date_disseminated=[gte]1992-01-09[lte]1992-01-09&limit=100&sort=date_disseminated,desc 20191118125603 https://www.fcc.gov/ecfs/search/filings?date_disseminated=%5Bgte%5D1992-01-09%5Blte%5D1992-01-09&limit=100&sort=date_disseminated,DESC warc/request - I5OL3NNFS3IQMIR7WBSTBCQSWGODBTOT - - 552 0 date_resolution_nanosecond.warc.gz'
    # ],
    # Pathological: Empty HTTP payload, header ends with single "\n"
    'empty_payload_header_ending_with_lf.arc.gz': [
        b'1,120,179,210)/test 20030801004548 http://210.179.120.1/test unk 200 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 222 0 empty_payload_header_ending_with_lf.arc.gz'
    ],
    'empty_record.arc.gz': [
        b'filedesc://live-20120312161414739-00234.arc 20120312161414 filedesc://live-20120312161414739-00234.arc warc/filedesc - VXEDWGPHSNERWHDOUD6YWRWNT4ZOLEX4 - - 154 0 empty_record.arc.gz',
        b'com,bfast,service)/bfast/serve?bfmid=1821322&bfpage=page_d_accueil&siteid=18015626 20120312163604 http://service.bfast.com/bfast/serve?bfmid=1821322&siteid=18015626&bfpage=page_d_accueil unk 410 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 145 154 empty_record.arc.gz'
    ],
    #from 42_0_20070519125725_crawl29-c/42_0_20070519230217_crawl31.arc.gz
    'formfeed_in_url.arc.gz': [
        b'filedesc://42_0_20070519230217_crawl31.arc.gz 20070519230217 filedesc://42_0_20070519230217_crawl31.arc.gz warc/filedesc - 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 159 0 formfeed_in_url.arc.gz',
        b'com,megaclick)/notf!%ca%9d%f5%99s%19%f1d%ef%96%03x%92%8d%a7%1d%99%f9!%d7%97/%8c%1c52%fa%f9%f2b%e2%89u%dc%ad2 20070519230830 http://www.megaclick.com:80/notf!\xca\x9d\xf5\x99s\x19\xf1d\xef\x96\x03X\x92\x8d\xa7\x1d\x99\xf9!\xd7\x97/\x8c\x1c52\xfa\xf9\xf2b\xe2\x89u\xdc\xad2#l\x8a\xae\xd9\xdf\xbd\x05;2z\x91\x10r%0C\xcf9\xbe text/html 404 QTPHGEGAVG7NTUMH3UQF2YGQHZ27VGML - - 445 159 formfeed_in_url.arc.gz'
    ],
    # ftp capture in resource record, with WARC-Block-Digest (wget)
    'ftp-resource-block-digest.warc.gz': [
        b'de,mayn,ftp)/pub/really_old_stuff/index.txt 20160803105717 ftp://ftp.mayn.de/pub/really_old_stuff/INDEX.txt application/octet-stream 226 A2QW3LECPALZHVBQJ75WFDLXTQEF3FGZ - - 491 0 ftp-resource-block-digest.warc.gz'
    ],
    # ftp capture in resource record, with neither payload nor block digest
    'ftp-resource-no-digest.warc.gz': [
        b'de,mayn,ftp)/pub/really_old_stuff/index.txt 20160803105717 ftp://ftp.mayn.de/pub/really_old_stuff/INDEX.txt application/octet-stream 226 A2QW3LECPALZHVBQJ75WFDLXTQEF3FGZ - - 442 0 ftp-resource-no-digest.warc.gz'
    ],
    # ftp capture in resource record, with WARC-Payload-Digest (Heritrix)
    'ftp-resource-payload-digest.warc.gz': [
        b'org,gnome,ftp)/header.html 20161231090454 ftp://ftp.gnome.org/HEADER.html application/octet-stream 226 DN7ET4FWNU6IBZAUAJM4STV74ORN4E4N - - 753 0 ftp-resource-payload-digest.warc.gz'
    ],
    'giant_html.warc.gz': [
        b'com,guide-fleurs)/site/partenaires.htm 20120121173511 http://www.guide-fleurs.com/site/partenaires.htm text/html 200 BGA6K3VEQVACI7KVTAGRNMBAPIYIGELF - - 1882583 0 giant_html.warc.gz'
    ],
     #from GR-033925-c/GR-034368.arc.gz
    'hex_instead_of_date.arc.gz': [
        b'filedesc://export/home2/19970801/GR-034368.arc 19700101000000 filedesc://export/home2/19970801/GR-034368.arc warc/filedesc - 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 161 0 hex_instead_of_date.arc.gz',
        b'se,ki,cbt)/wwwcnt/staff/bergman.jan - http://www.cbt.ki.se:80/wwwCNT/Staff/bergman.jan/ text/html 200 6SIKE3B5MYK545CZXFGHULO6EXKYTCMG - - 993 161 hex_instead_of_date.arc.gz'
    ],
    #from live-20120312105341306-00165-20120312171822397/live-20120312161414739-00234.arc.gz
    'meta_tag_FI.arc.gz': [
        b'filedesc://live-20120312161414739-00234.arc 20120312161414 filedesc://live-20120312161414739-00234.arc warc/filedesc - VXEDWGPHSNERWHDOUD6YWRWNT4ZOLEX4 - - 154 0 meta_tag_FI.arc.gz',
        b'ru,peskomment)/img/yandex.png 20120312161555 http://peskomment.ru/IMG/yandex.png text/html 404 GPQYK2UWAU4ZOITDYRRE2DJ67NX74QN6 - FI 748 154 meta_tag_FI.arc.gz'
    ],
    #from live-20120312105341306-00165-20120312171822397/live-20120312161414739-00234.arc.gz
    'meta_tag_I.arc.gz': [
        b'filedesc://live-20120312161414739-00234.arc 20120312161414 filedesc://live-20120312161414739-00234.arc warc/filedesc - VXEDWGPHSNERWHDOUD6YWRWNT4ZOLEX4 - - 154 0 meta_tag_I.arc.gz',
        b'us,pa,butler,co)/robots.txt 20120312162156 http://co.butler.pa.us/robots.txt text/html 403 3RFKV4YVRVRFMAVXQO35WTW6K4Q3GO4H - I 1096 154 meta_tag_I.arc.gz'
    ],
    #from NO404-WKP-20131104215558-crawl345/NO404-WKP-20131104222227-08103.warc.gz
    'meta_tag_large.warc.gz': [
        b'com,richmondstrikers)/alumni/index_e.html 20131104222633 http://www.richmondstrikers.com/Alumni/index_E.html text/html 200 U7ST7H2CUXSLGCOYR3KT5POAPZI3KY7B - - 21796 0 meta_tag_large.warc.gz'
    ],
    'missing_content_type.warc.gz': [
        b'com,example)/missing_content_type 20150415034052 http://example.com/missing_content_type unk 200 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 267 0 missing_content_type.warc.gz'
    ],
    'negative_content_length.arc.gz': [
        b'filedesc://live-20120420173851608-04730.arc 20120420173851 filedesc://live-20120420173851608-04730.arc warc/filedesc - VXEDWGPHSNERWHDOUD6YWRWNT4ZOLEX4 - - 155 0 negative_content_length.arc.gz',
        b'com,lastdaywatchers)/robots.txt 20120420180002 http://www.lastdaywatchers.com/robots.txt text/html 301 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ S - 244 155 negative_content_length.arc.gz',
        b'com,diggheadlines)/robots.txt 20120420180002 http://diggheadlines.com/robots.txt unk 200 QUD4X4EYJB6TOGMGIXCFKF4Y4MOAL5GS - - 103 520 negative_content_length.arc.gz'
    ],
    #from INA-HISTORICAL-2002-GROUP-EVL-20100812000000-00001-c/INA-HISTORICAL-2002-GROUP-FFM-20100812000000-00000.arc.gz.
    # We put a non-ascii char field like the java version, but we utf8-encode the character. Also, the surt seems incorrect. 
    # It seems like we should convert the surt to utf-8 before percent encoding..
    'non_ascii_url.arc.gz': [
        b'filedesc://INA-HISTORICAL-2002-GROUP-FFM-20100812000000-00000.arc 20100812000000 filedesc://INA-HISTORICAL-2002-GROUP-FFM-20100812000000-00000.arc warc/filedesc - VXEDWGPHSNERWHDOUD6YWRWNT4ZOLEX4 - - 168 0 non_ascii_url.arc.gz',
        b'fr,free,arevebebe)/php3/selcateg.php3?selec=%e9cole 20021108114510 http://arevebebe.free.fr/php3/selcateg.php3?selec=\xe9cole text/html 200 IRZDAFOGADI2OCQFHJGUBL6BELKT37C7 - - 2528 168 non_ascii_url.arc.gz'
    ],
    'password-protected-no-meta.warc.gz': [
        b'au,edu,unimelb,youngscholars)/ 20130813000800 http://youngscholars.unimelb.edu.au/ text/html 200 KPN526ULL7I6IELN2N6QWQUE2RPS335P - P 3494 0 password-protected-no-meta.warc.gz'
    ],
    #from ARCHIVEIT-3007-NONE-10537-20140331214316874-00000-desktop-nlevitt.sf.archive.org-6440.warc.gz
    'password-protected.warc.gz': [
        b'com,facebook)/login.php?login_attempt=1 20140331214328 https://www.facebook.com/login.php?login_attempt=1 text/html 200 I45Q4NNB7NJJQ6CULNCSXQBAYSDTYB7U - P 7147 0 password-protected.warc.gz'
    ],
    #from webgroup-20100529181442-00026/ARCHIVEIT-788-MONTHLY-AUTOCW-20091227192605-00091-crawling09.us.archive.org-8094.warc.gz
    'revisit_without_sha1.warc.gz': [
        b'edu,ucla,cs,ftp)/tech-report/198_-reports/860078.pdf 20091227192621 ftp://ftp.cs.ucla.edu/tech-report/198_-reports/860078.pdf warc/revisit - - - - 280 0 revisit_without_sha1.warc.gz'
    ],
    #from NARA-PEOT-2004-20041017204448-01850-crawling009-c/NARA-PEOT-2004-20041017235648-01294-crawling007.archive.org.arc.gz
    'spaces_in_url.arc.gz': [
        b'filedesc://NARA-PEOT-2004-20041017235648-01294-crawling007.archive.org.arc 20041017235648 filedesc://NARA-PEOT-2004-20041017235648-01294-crawling007.archive.org.arc warc/filedesc - WY7RK37U2G245OCZ4HVI36VUW4RKNECH - - 784 0 spaces_in_url.arc.gz',
        b'gov,fdic)/call_tfr_rpts/toccallreport1.asp?+trust+of+cheneyville+++++++++++++++++++++++++++++++++&paddr=main%20street%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20&pcert=16445&pcity=cheneyville+++++++++++++++++++&pcmbqtrend=09/30/2002&pdocket=0&pinstitution=the+farmers+bank+&pstalp=la&pzip5=71325 20041018000129 http://www3.fdic.gov/Call_tfr_rpts/toccallreport1.asp?pCert=16445&pDocket=0&pcmbQtrEnd=09%2F30%2F2002&paddr=MAIN%20STREET%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20&pCity=CHENEYVILLE+++++++++++++++++++&pStalp=LA&pzip5=71325&pInstitution=The+Farmers+Bank+%26+Trust+of+Cheneyville+++++++++++++++++++++++++++++++++ text/html 400 7JKONWAKLVFR7BZOIT2UE3NZIMYOD54S - - 409 784 spaces_in_url.arc.gz'
    ],
    #from MP3-CRAWL-crawl05.20031219201259-c/MP3-CRAWL-crawl05.20031219215024.arc.gz. Empty HTTP payload, header ends with single "\r\n"
    'transposed_header.arc.gz': [
        b'filedesc:///2/mp3_arcs/MP3-CRAWL-crawl05.20031219215024 20031219215024 filedesc:///2/mp3_arcs/MP3-CRAWL-crawl05.20031219215024 warc/filedesc - 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 163 0 transposed_header.arc.gz',
        b'com,mp3,play)/cgi-bin/play/play.cgi/aaiaqo93mqdabg5vcm1qbaaaafj88quauqeaaabdnyyxp6sbry55rya.wo2ewl.61xo-/losing_time.mp3 20031219215023 http://play.mp3.com/cgi-bin/play/play.cgi/AAIAQo93MQDABG5vcm1QBAAAAFJ88QUAUQEAAABDNyyxP6SbRY55RYa.wO2ewL.61xo-/Losing_Time.mp3 text/plain 302 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 347 163 transposed_header.arc.gz'
    ],
    'uncompressed.arc': [
        b'filedesc://51_23_20110804181044_crawl101.arc.gz 20110804181044 filedesc://51_23_20110804181044_crawl101.arc.gz warc/filedesc - 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 161 0 uncompressed.arc',
        b'vn,rolo,art)/a/chi-tiet/021826271565622/ngoc-trinh-xinh-tuoi-o-hoi-an 20110804181044 http://art.rolo.vn:80/a/chi-tiet/021826271565622/ngoc-trinh-xinh-tuoi-o-hoi-an unk 404 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 229 162 uncompressed.arc',
        b'de,sueddeutsche)/muenchen/manu-chao-in-muenchen-che-guitarra-1.1114509-2 20110804181044 http://www.sueddeutsche.de:80/muenchen/manu-chao-in-muenchen-che-guitarra-1.1114509-2 text/html 200 ZMBIXCVTXG2CNEFAZI753FJUXJUQSI2M - A 78939 392 uncompressed.arc',
        b'com,monsterindia,jobs)/details/9660976.html 20110804181044 http://jobs.monsterindia.com:80/details/9660976.html text/html 200 BQJDX42R5GFX4OIXPGNHZG3QFM5X3KQR - - 51406 79332 uncompressed.arc'
    ],
    'uncompressed.warc': [
        b'warcinfo:/uncompressed.warc/archive-commons.0.0.1-SNAPSHOT-20120112102659-python 20110307082936 warcinfo:/uncompressed.warc/archive-commons.0.0.1-SNAPSHOT-20120112102659-python warc-info - Z6BGWH54O6X5637RCT5X6E2K5257JM6C - - 919 0 uncompressed.warc',
        b'au,edu,icms,alumni)/s/1278/index.aspx?cid=256&cid=421&cid=46&gid=1&gid=1&gid=1&mid=3054&pgid=3&pgid=8&pgid=94&returnurl=http://alumni.icms.edu.au/s/1278/index.aspx?sid=1278&returnurl=http://alumni.icms.edu.au/s/1278/index.aspx?sid=1278&sid=1278&verbiagebuilder=1 20110307082935 http://alumni.icms.edu.au/s/1278/index.aspx?sid=1278&gid=1&returnurl=http%3a%2f%2falumni.icms.edu.au%2fs%2f1278%2findex.aspx%3fsid%3d1278%26gid%3d1%26returnurl%3dhttp%3a%2f%2falumni.icms.edu.au%2fs%2f1278%2findex.aspx%3fsid%3d1278%26gid%3d1%26verbiagebuilder%3d1%26pgid%3d94%26cid%3d256%26mid%3d3054%26pgid%3d3%26cid%3d421&pgid=8&cid=46 warc/request - BYNHD3QZZY5BEQCFNZE2CTC5FO6U5NYU - - 1891 923 uncompressed.warc'
    ],
    # response record has chunked response. WARC header has incorrect WARC-Payload-Digest ZSSZNM66RWQWZ7FMNEP2XEAORAULQHMY (computed without removing Transfer-Encoding)
    # created with wget 1.14
    'wget_ia.warc.gz': [
        b'warcinfo:/wget_ia.warc.gz/archive-commons.0.0.1-SNAPSHOT-20120112102659-python 20140314173216 warcinfo:/wget_ia.warc.gz/archive-commons.0.0.1-SNAPSHOT-20120112102659-python warc-info - 3YXFFQSTALFMTNNPD7CF6GCBK6NMGTCN - - 414 0 wget_ia.warc.gz',
        b'org,archive)/ 20140314173216 https://archive.org/ text/html 200 NWFY5M3576VSQ4Y2S2QEXAIUN2IWOK6Y - - 6891 414 wget_ia.warc.gz'
    ],
    # some warcs from webrecorder captures from ~2015 (and earlier?) contain empty gzip members
    'empty-gzips.warc.gz': [
        b'warcinfo:/empty-gzips.warc.gz/archive-commons.0.0.1-SNAPSHOT-20120112102659-python 20171006165514 warcinfo:/empty-gzips.warc.gz/archive-commons.0.0.1-SNAPSHOT-20120112102659-python warc-info - CBDY3U5FHZ7DOZMT3B3DSMXZ5HGIEEGR - - 344 282 empty-gzips.warc.gz',
        b'com,example)/ 20171006165514 http://example.com/ text/html 200 B2LTWWPUOYAH7UIPQ7ZUPQ4VMBSVC36A - - 1109 626 empty-gzips.warc.gz',
        b'com,example)/ 20171006165514 http://example.com/ warc/request - GSRRZI5PK3M36H32WP4VJDGDFQERBR3Q - - 423 1735 empty-gzips.warc.gz',
        b'warcinfo:/empty-gzips.warc.gz/archive-commons.0.0.1-SNAPSHOT-20120112102659-python 20171006165521 warcinfo:/empty-gzips.warc.gz/archive-commons.0.0.1-SNAPSHOT-20120112102659-python warc-info - CBDY3U5FHZ7DOZMT3B3DSMXZ5HGIEEGR - - 342 2440 empty-gzips.warc.gz',
        b'com,example)/ 20171006165521 http://example.com/ warc/revisit - B2LTWWPUOYAH7UIPQ7ZUPQ4VMBSVC36A - - 637 2782 empty-gzips.warc.gz',
        b'com,example)/ 20171006165521 http://example.com/ warc/request - GSRRZI5PK3M36H32WP4VJDGDFQERBR3Q - - 424 3419 empty-gzips.warc.gz',
        b'warcinfo:/empty-gzips.warc.gz/archive-commons.0.0.1-SNAPSHOT-20120112102659-python 20171006165527 warcinfo:/empty-gzips.warc.gz/archive-commons.0.0.1-SNAPSHOT-20120112102659-python warc-info - CBDY3U5FHZ7DOZMT3B3DSMXZ5HGIEEGR - - 342 4689 empty-gzips.warc.gz',
        b'com,example)/ 20171006165527 http://example.com/ warc/revisit - B2LTWWPUOYAH7UIPQ7ZUPQ4VMBSVC36A - - 639 5031 empty-gzips.warc.gz',
        b'com,example)/ 20171006165527 http://example.com/ warc/request - GSRRZI5PK3M36H32WP4VJDGDFQERBR3Q - - 421 5670 empty-gzips.warc.gz'
    ]
}

# {warc-filename: output-of-cdx_writer.py-with-no-options, ...}
warcs_defaults = {
    # '16_digit_date.arc.gz': [
    #     b'com,afp)/home/img/es.gif 20000823054100 http://www.afp.com:80/home/img/es.gif image/gif 200 TUQLSV5PWCWHL2X3O67JULYLMWXGA252 - - 936 168 16_digit_date.arc.gz'
    # ],
    # '18_digit_date.arc.gz': [
    #     b'com,spaceports,mars)/~jddp/images/links_off.gif 20000918002300 http://mars.spaceports.com:80/~jddp/images/links_off.gif image/gif 200 V7FZGUGSTVX4EKWAT46CTBB47KSIYO7F - - 1165 181 18_digit_date.arc.gz'
    # ],
    # from ARCHIVEIT-7855-TEST-JOB270756-SEED1365208-20170303022116385-00000-qh0i1erc.warc.gz written by warcprox 2.1b1 written by warcprox 2.1b1.dev54
    '304-response.warc.gz': [],
    # from WEB-20170329205740560-00000-11979~macbook-pro.monkeybrains.net~6440.warc.gz written by Heritrix/3.3.0-SNAPSHOT-2017-03-14T22:20:41Z
    '304-revisit.warc.gz': [],
    # 'alexa_charset_in_header.arc.gz': [
    #     b'fr,allocine,free)/tv/cineaction.asp 20000824015105 http://free.allocine.fr:80/tv/cineaction.asp text/html 200 YSO3GBFJ7KRO3OPF7J43J4NMM4LVR7ZY - - 3974 168 alexa_charset_in_header.arc.gz'
    # ],
    # empty mimetype field in ARC header, non-HTTP content. 3.x emitted no statuscode. 4.x emits assumed 200.
    'alexa_short_header.arc.gz': [
        b'net,killerjo)/robots.txt 20110804181142 http://www.killerjo.net:80/robots.txt unk 200 YZI2NMZ5ILYICUL3PNYVYQR3KI2YY5EH - - 139 161 alexa_short_header.arc.gz'
    ],
    'arc_v1_with_v2_header.arc.gz': [
        b'com,cdnow)/cgi-bin/mserver/pagename=/rp/cdn/find/discography.html/artistid=henderson*joe/select=music 20001110112000 http://www.cdnow.com:80/cgi-bin/mserver/pagename=/RP/CDN/FIND/discography.html/artistid=HENDERSON*JOE/select=music text/html 200 Z7XLU7KXZVH3AAC6ZZLMMRVWPHC44ALO - - 8884 179 arc_v1_with_v2_header.arc.gz',
    ],
    # moved to test_fields.py
    # 'bad_mime_type.arc.gz': [
    #     b'net,naver,cafethumb)/20101223_84/qkrgns3_129303386816936xuq_jpg/imag0030_qkrgns3.jpg 20120407152447 http://cafethumb.naver.net/20101223_84/qkrgns3_129303386816936xUq_jpg/imag0030_qkrgns3.jpg unk 200 OUK52MTLKPEA6STHTFFPFI2JP7G4QBUZ - - 3587 153 bad_mime_type.arc.gz'
    # ],
    'bad_unicode_host.arc.gz': [
        b'net,82,t%ef%bf%bd%04)/ 20080509130938 http://www.t%EF%BF%BD%04.82.net/ text/html 200 V6CPFAFQFDRK2BWCGRXEZYKAGOUMWYM5 - - 416 158 bad_unicode_host.arc.gz'
    ],
    'bad_url_with_colon_1.arc.gz': [
        b"http://JavaScript:Wtop('www.pick2hand.com/index2.html') 20071008060921 http://JavaScript:Wtop('www.pick2hand.com/index2.html') text/html 200 DANDEM27HUMJBSIAEPFZR5BB2LMNXROO - - 528 0 bad_url_with_colon_1.arc.gz"
    ],
    # besides anomally in URL field, Content-Length: 50191 includes the last \n in the record (supposed to be a padding byte after content)
    'bad_url_with_colon_2.arc.gz': [
        b'http://mhtml:d.hatena.ne.jp/images/top/greenpower_logo.gif 20071121164820 http://mhtml:d.hatena.ne.jp/images/top/greenpower_logo.gif text/html 200 2RFE734TL4XU6RQQOSM2BVPRGS5KGJTS - - 14465 0 bad_url_with_colon_2.arc.gz'
    ],
    'carriage_return_in_url.arc.gz': [
        b'org,cheapchicks)/cgi-bin/count/slcnt.cgi?c=3 20070216134117 http://cheapchicks.org/cgi-bin/count/slcnt.cgi?c=3 text/html 200 DRN2R2KFMNP6SQ6MYXFGSW366YL2IDOA - - 666 171 carriage_return_in_url.arc.gz'
    ],
    'chardet_failure_url.arc.gz': [
        b'cn,com,pconline,guide)/gamecomment/post.jsp?column=netgame&topic=%ce%d2%c3%c7%d7%f6%d6%f7%b5%c4%ca%c0%b4%fa%b5%bd%c0%b4%c1%cb%a3%a1%a1%b6%c8%d9%d2%ab%a1%b7%b7%a8%b5%e4%d5q%c9%fa%a3%a1 20040711214255 http://guide.pconline.com.cn:80/gamecomment/post.jsp?column=netgame&topic=\xce\xd2\xc3\xc7\xd7\xf6\xd6\xf7\xb5\xc4\xca\xc0\xb4\xfa\xb5\xbd\xc0\xb4\xc1\xcb\xa3\xa1\xa1\xb6\xc8\xd9\xd2\xab\xa1\xb7\xb7\xa8\xb5\xe4\xd5Q\xc9\xfa\xa3\xa1 text/html 400 YVY3QUSAB6EOL5HYRV3CNKRMZZ6U6K2E - - 485 153 chardet_failure_url.arc.gz'
    ],
    'crlf_at_1k_boundary.warc.gz': [
        b'nz,co,tradeaboat,whitiangamarine)/emailafriend.aspx?item=h4siagw4x00a/wfwao/9gaxg6utmkolwv1zy9nohybsaoj36okttm/cdglv9et4wgw8ywbkoacccfsjvdmf7bge+ke8edgs5h4ib0rue96yj2/r5lixmy1sueue5iihmyms9jl9femizgo6yaew0fx+snckd5d+ow5216i0sj9yb0pzj/i/3z3mannav042wjyfyugogpn6yv2wzgueerk5fqi+msasd88rtsytzkszuc/mtpdowhevxiy3n2+r1n6q9utfvekuy5bonzpqy7blk93yj9dnviit0zjmshgotxc0nuywionfpixfogmm8y6i3rfxxqxd5p95qmiogdi1rvpgkcav+go4nz4r/caicl697pcwfkcqyfw5zts74+snrdessbdz2quceotydcw2gh3hogkrrupiqn9hfdvsb2p3hxp/ygkh9w6+d8jp7tylmalvnjjevst/6wlbqrhwrsnlpxntjxqzrtw7z8e/+o5bfsb6hgwfxzulqz2rnnfvazomgkckthoprtba6cp5ifb8j8sfov7pvwifngclbr28ekmjaebqrznblb4njweisomyenibp/qlvpv4sqarzduhs1qri9toq/toiasrlkpq+sdsbuzqjxij9b/tjgx8biqe129tdob0bdhtexwqq1aoaasxmtqddrykqcrvckjfh1ayszhyl9p6xs6lwmalo2mygxnzegkrvpfr5c/edjp6hr/28egr4fdxyyrwaumhoprqgxyjtq7nqwv7m8jyyvxcfgpx6kz6ftu4nmbahpuhgxd/eddp5y3duicjbcaymmvvmojqxmxb8cpsytv9zcu1rn5ehrp2iypudy+6ihhacaaa= 20110218233256 http://whitiangamarine.tradeaboat.co.nz/emailAFriend.aspx?item=H4sIAGW4X00A%2fwFwAo%2f9gaXg6UTMkoLWV1Zy9nOhybsaOj36okTTM%2fCdGlV9et4wGW8ywbKoacCcFSjvDmf7BgE%2bke8eDGs5H4ib0RuE96Yj2%2fR5LIXmy1SUEue5IiHmYmS9jl9femiZGo6yAeW0fX%2bSnCkd5D%2bOW5216i0SJ9yb0PZJ%2fI%2f3z3manNAv042wJYFyUgOGpN6yV2wZGUEERk5FQI%2bmSASd88RTsytzksZuC%2fmTpDowhevXiY3N2%2br1n6Q9utfvEKuy5bonZPqy7BlK93yJ9DnviiT0ZJMsHGOTXC0NUywIonFpIXfogmm8y6I3RfXxQXD5p95qmiogdI1rvPgKCaV%2bgO4nZ4r%2fCAicl697pcwFKCQyFW5ZTS74%2bSnrdEssBdz2quceotYDcW2GH3hogkrRupiqN9hFdVsb2p3HXP%2fYGkH9W6%2bD8jp7TyLmALvnJJevST%2f6wlbQRhWrsNlPXnTjxQZrTw7z8E%2f%2bo5BFsb6HgWfXzULQZ2RnNFvAZOMgkcKtHopRTbA6cp5ifB8j8sFoV7PVwifNgcLBR28EKMjAeBqRZnBlB4nJwEISomyeNIBP%2fQlvpV4sqArZdUhs1qRi9TOQ%2fToiaSrlKpq%2bSdSbuZqjXIJ9b%2ftjgx8biQe129TDOB0BDHtEXwqq1aoaASxmTqddrYKqCRvcKjfH1aYSZHyL9p6xS6LwMAlO2myGxnZeGkrVpfr5C%2fEDJp6HR%2f28EgR4fdXyyRWauMhoPrQgXYJTq7NQwv7m8JYyvxCfGpX6Kz6ftu4NMBAHPuhGxd%2fEDDP5y3DUIcJBCAyMMvvMOJQXMXb8cpsyTv9ZcU1RN5ehrp2iyPudY%2b6iHHACAAA%3d text/html 200 M4VJCCJQJKPACSSSBHURM572HSDQHO2P - - 2588 0 crlf_at_1k_boundary.warc.gz'
    ],
    'crlf_at_1k_boundary_2.warc.gz': [
        b'au,com,grandtourer)/aspx/login.aspx?4=h6vklmshqnbpvsscb7x7iu2/luokwckr5nsukefi3ygag1wtqor9vtiwv+anh9su4shtqmrrjy53dhqpxif+vjqkb+tajvfhn/sn1oqgaxly4i1ciwbi6jbk+i0fqqn44wt18szrgn95ygnruk9baymdquzchh7i/pak180zcfccrud+lqmmukvlvg0qoq6kvbos8dqo3mh5unwoclxiid2+mbma2rfp/015+o5+dnrq/umof3aettvsy7i/bcmgkbn/6wqknr04kfi4ppwjig2vcw4av8hj2fqbo+3jutdryfgyulizuqjebrh0lmah9sgkrpomwa0hgzmvf1ahoyqbvnbwujeekckxrydnd+dtxyozqlpygn/gcedbkoubmmmldsl+stl4qzomxngk3xnxiw+/csq/pwyimcbtdl/fxvnj6j4l3m5v66mjhxmyzk/wfp7spfzeghl+x4ih9dzzl8nqr/+ma7e6jhmyx4/dwkresqh3mzmiqddmdp6cjtnxapulfamv/tdy1vgjdl4pbiasartibf4nnxlglpvcy+cm3j83nybyytxbrx9+x1vcvnvpo8sipspuyp8xi0glnsmaw/u+owll28euzdlvanmz2j0rcdhtqkyejfhn/rm4z1gkhwn2rexkykbgtnuppthr08v6sur9kagw9dzdyut0go9fjshgpbmnm0uaujtzkshhi0uriz2cnn+arsppeayooy3yedrv7vklewh6mj3yjqfzwj4tbq75wecrm9gw4p+7uwal4wc92gjdip7g1p2cm4vbtvahp1ntq+shd4oot5r6hza2igo85st3ftgfvfj7eolin+dixrjdwa== 20120422095915 https://www.grandtourer.com.au/Aspx/Login.aspx?4=H6VKLMsHqnBpvsscB7x7Iu2%2fLUOKwCKr5nsukefI3ygAG1WTqOR9vtiWv%2banh9sU4sHTQmRRJY53DHQpXiF%2bVjqKB%2btaJvfHn%2fSN1OQgaxlY4i1Ciwbi6jbK%2bI0fQqn44Wt18szRgN95ygNRUK9BaYMdqUzChH7I%2fpAk180zCFCCRUD%2bLqMMuKvLVg0qOQ6Kvbos8DqO3MH5UnwOcLxiID2%2bmBMA2Rfp%2f015%2bo5%2bDNRq%2fUMOF3aETtvSY7i%2fbCmGKBn%2f6WqkNr04Kfi4PPWJIg2VCw4AV8hj2FqbO%2b3JUtdRYfGYulizuQJEbrh0LMah9sGKRPomWA0hgZmvf1AHoYqbVNbwUJeEKCKxrYdND%2bDtxyOzQlpygN%2fgCeDbKOuBMMMLdSl%2bsTl4qZoMXnGK3XNxiw%2b%2fcsq%2fPWyIMCBtdl%2ffXvnJ6J4L3M5v66mjhXmyZk%2fwfp7SpfzegHL%2bX4iH9DZzl8nqr%2f%2bmA7E6JHmyX4%2fDWKrEsqH3MZMIqddmDp6cJtnxAPULfAmv%2fTDY1VGJdl4PBIASArTIBF4nnXLglpvcy%2bcm3j83nyByyTxbRX9%2bX1VcVNvPo8SIpSpuYP8xi0GlNsMaW%2fu%2bowll28EUzDLVAnMz2j0rcdhTqKYEJfhN%2frm4Z1gKhwn2REXKykBGTnupPtHR08V6Sur9kAgW9DZdyUt0Go9fJshGPBmNm0uAUjtzkshhI0UrIz2cnn%2bArspPeaYOOY3YEdrV7VKlEWh6Mj3yjQFZwj4TbQ75WECrM9Gw4p%2b7uWaL4wc92gjDiP7G1P2cM4vBTVAHP1nTQ%2bShD4OoT5r6hZA2igo85St3ftgfvfJ7eOLin%2bdixRJdwA%3d%3d text/html 200 5STDGW7HDWZQ4TPS4GPBOL3TEG7NQRHE - - 6934 0 crlf_at_1k_boundary_2.warc.gz'
    ],
    'empty_payload_header_ending_with_lf.arc.gz': [
        b'1,120,179,210)/test 20030801004548 http://210.179.120.1/test unk 200 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 222 0 empty_payload_header_ending_with_lf.arc.gz'
    ],
    'empty_record.arc.gz': [
        b'com,bfast,service)/bfast/serve?bfmid=1821322&bfpage=page_d_accueil&siteid=18015626 20120312163604 http://service.bfast.com/bfast/serve?bfmid=1821322&siteid=18015626&bfpage=page_d_accueil unk 410 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 145 154 empty_record.arc.gz'
    ],
    'formfeed_in_url.arc.gz': [
        b'com,megaclick)/notf!%ca%9d%f5%99s%19%f1d%ef%96%03x%92%8d%a7%1d%99%f9!%d7%97/%8c%1c52%fa%f9%f2b%e2%89u%dc%ad2 20070519230830 http://www.megaclick.com:80/notf!\xca\x9d\xf5\x99s\x19\xf1d\xef\x96\x03X\x92\x8d\xa7\x1d\x99\xf9!\xd7\x97/\x8c\x1c52\xfa\xf9\xf2b\xe2\x89u\xdc\xad2#l\x8a\xae\xd9\xdf\xbd\x05;2z\x91\x10r%0C\xcf9\xbe text/html 404 QTPHGEGAVG7NTUMH3UQF2YGQHZ27VGML - - 445 159 formfeed_in_url.arc.gz'
    ],
    'ftp-resource-block-digest.warc.gz': [
        b'de,mayn,ftp)/pub/really_old_stuff/index.txt 20160803105717 ftp://ftp.mayn.de/pub/really_old_stuff/INDEX.txt application/octet-stream 226 A2QW3LECPALZHVBQJ75WFDLXTQEF3FGZ - - 491 0 ftp-resource-block-digest.warc.gz'
    ],
    'ftp-resource-no-digest.warc.gz': [
        b'de,mayn,ftp)/pub/really_old_stuff/index.txt 20160803105717 ftp://ftp.mayn.de/pub/really_old_stuff/INDEX.txt application/octet-stream 226 A2QW3LECPALZHVBQJ75WFDLXTQEF3FGZ - - 442 0 ftp-resource-no-digest.warc.gz'
    ],
    'ftp-resource-payload-digest.warc.gz': [
        b'org,gnome,ftp)/header.html 20161231090454 ftp://ftp.gnome.org/HEADER.html application/octet-stream 226 DN7ET4FWNU6IBZAUAJM4STV74ORN4E4N - - 753 0 ftp-resource-payload-digest.warc.gz'
    ],
    'giant_html.warc.gz': [
        b'com,guide-fleurs)/site/partenaires.htm 20120121173511 http://www.guide-fleurs.com/site/partenaires.htm text/html 200 BGA6K3VEQVACI7KVTAGRNMBAPIYIGELF - - 1882583 0 giant_html.warc.gz'
    ],
    'hex_instead_of_date.arc.gz': [
        b'se,ki,cbt)/wwwcnt/staff/bergman.jan - http://www.cbt.ki.se:80/wwwCNT/Staff/bergman.jan/ text/html 200 6SIKE3B5MYK545CZXFGHULO6EXKYTCMG - - 993 161 hex_instead_of_date.arc.gz',
    ],
    'meta_tag_FI.arc.gz': [
        b'ru,peskomment)/img/yandex.png 20120312161555 http://peskomment.ru/IMG/yandex.png text/html 404 GPQYK2UWAU4ZOITDYRRE2DJ67NX74QN6 - FI 748 154 meta_tag_FI.arc.gz'
    ],
    'meta_tag_I.arc.gz': [
        b'us,pa,butler,co)/robots.txt 20120312162156 http://co.butler.pa.us/robots.txt text/html 403 3RFKV4YVRVRFMAVXQO35WTW6K4Q3GO4H - I 1096 154 meta_tag_I.arc.gz'
    ],
    'meta_tag_large.warc.gz': [
        b'com,richmondstrikers)/alumni/index_e.html 20131104222633 http://www.richmondstrikers.com/Alumni/index_E.html text/html 200 U7ST7H2CUXSLGCOYR3KT5POAPZI3KY7B - - 21796 0 meta_tag_large.warc.gz'
    ],
    'missing_content_type.warc.gz': [
        b'com,example)/missing_content_type 20150415034052 http://example.com/missing_content_type unk 200 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 267 0 missing_content_type.warc.gz'
    ],
    'negative_content_length.arc.gz': [
        b'com,lastdaywatchers)/robots.txt 20120420180002 http://www.lastdaywatchers.com/robots.txt text/html 301 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ S - 244 155 negative_content_length.arc.gz'
    ],
     # from channel4-www.channel4.com--20140218-1632/channel4-www.channel4.com--20140218-1632-20140218163723-00000-72ebc14a-e463-4284-8b77-2bb1cbf89f0f.warc.gz
     # no WARC-Payload-Digest, HTTP Content-Length: 5486 is smaller than actual 23856. 3.x computed SHA1 5YMS42S5QTOOT5OMMYSXM23ZLZJB6KPR from full content. 4.x computes SHA1 for the 5486 bytes.
    'no_sha1_whitespace_in_contenttype.warc.gz': [
        b'com,channel4)/static/globalnav/css/globalnav.css 20140218163736 http://www.channel4.com/static/globalnav/css/globalnav.css text/css 200 YZ2N3TG6XHSI2ECYLLF7OJKLIVU5BFYE - - 5254 0 no_sha1_whitespace_in_contenttype.warc.gz',
    ],
    'non_ascii_url.arc.gz': [
        b'fr,free,arevebebe)/php3/selcateg.php3?selec=%e9cole 20021108114510 http://arevebebe.free.fr/php3/selcateg.php3?selec=\xe9cole text/html 200 IRZDAFOGADI2OCQFHJGUBL6BELKT37C7 - - 2528 168 non_ascii_url.arc.gz'
    ],
    'password-protected-no-meta.warc.gz': [
        b'au,edu,unimelb,youngscholars)/ 20130813000800 http://youngscholars.unimelb.edu.au/ text/html 200 KPN526ULL7I6IELN2N6QWQUE2RPS335P - P 3494 0 password-protected-no-meta.warc.gz'
    ],
    'password-protected.warc.gz': [
        b'com,facebook)/login.php?login_attempt=1 20140331214328 https://www.facebook.com/login.php?login_attempt=1 text/html 200 I45Q4NNB7NJJQ6CULNCSXQBAYSDTYB7U - P 7147 0 password-protected.warc.gz',
    ],
    'revisit_without_sha1.warc.gz': [
        b'edu,ucla,cs,ftp)/tech-report/198_-reports/860078.pdf 20091227192621 ftp://ftp.cs.ucla.edu/tech-report/198_-reports/860078.pdf warc/revisit - - - - 280 0 revisit_without_sha1.warc.gz'
    ],
    'spaces_in_url.arc.gz': [
        b'gov,fdic)/call_tfr_rpts/toccallreport1.asp?+trust+of+cheneyville+++++++++++++++++++++++++++++++++&paddr=main%20street%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20&pcert=16445&pcity=cheneyville+++++++++++++++++++&pcmbqtrend=09/30/2002&pdocket=0&pinstitution=the+farmers+bank+&pstalp=la&pzip5=71325 20041018000129 http://www3.fdic.gov/Call_tfr_rpts/toccallreport1.asp?pCert=16445&pDocket=0&pcmbQtrEnd=09%2F30%2F2002&paddr=MAIN%20STREET%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20&pCity=CHENEYVILLE+++++++++++++++++++&pStalp=LA&pzip5=71325&pInstitution=The+Farmers+Bank+%26+Trust+of+Cheneyville+++++++++++++++++++++++++++++++++ text/html 400 7JKONWAKLVFR7BZOIT2UE3NZIMYOD54S - - 409 784 spaces_in_url.arc.gz'
    ],
    'transposed_header.arc.gz': [
        b'com,mp3,play)/cgi-bin/play/play.cgi/aaiaqo93mqdabg5vcm1qbaaaafj88quauqeaaabdnyyxp6sbry55rya.wo2ewl.61xo-/losing_time.mp3 20031219215023 http://play.mp3.com/cgi-bin/play/play.cgi/AAIAQo93MQDABG5vcm1QBAAAAFJ88QUAUQEAAABDNyyxP6SbRY55RYa.wO2ewL.61xo-/Losing_Time.mp3 text/plain 302 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 347 163 transposed_header.arc.gz'
    ],
    'uncompressed.arc': [
        b'vn,rolo,art)/a/chi-tiet/021826271565622/ngoc-trinh-xinh-tuoi-o-hoi-an 20110804181044 http://art.rolo.vn:80/a/chi-tiet/021826271565622/ngoc-trinh-xinh-tuoi-o-hoi-an unk 404 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 229 162 uncompressed.arc',
        b'de,sueddeutsche)/muenchen/manu-chao-in-muenchen-che-guitarra-1.1114509-2 20110804181044 http://www.sueddeutsche.de:80/muenchen/manu-chao-in-muenchen-che-guitarra-1.1114509-2 text/html 200 ZMBIXCVTXG2CNEFAZI753FJUXJUQSI2M - A 78939 392 uncompressed.arc',
        b'com,monsterindia,jobs)/details/9660976.html 20110804181044 http://jobs.monsterindia.com:80/details/9660976.html text/html 200 BQJDX42R5GFX4OIXPGNHZG3QFM5X3KQR - - 51406 79332 uncompressed.arc'
    ],
    'uncompressed.warc': [],
    'wget_ia.warc.gz': [
        b'org,archive)/ 20140314173216 https://archive.org/ text/html 200 NWFY5M3576VSQ4Y2S2QEXAIUN2IWOK6Y - - 6891 414 wget_ia.warc.gz'
    ],
    'tweet.warc.gz': [
        b'com,twitter)/zionfather/status/849230566553788416 20170404120905 https://twitter.com/zionfather/status/849230566553788416 application/json - BE7OMHMDUH6CI5OJXBC4D5AOFFZETVN2 - - 1168 0 tweet.warc.gz'
    ],
    'empty-gzips.warc.gz': [
        b'com,example)/ 20171006165514 http://example.com/ text/html 200 B2LTWWPUOYAH7UIPQ7ZUPQ4VMBSVC36A - - 1109 626 empty-gzips.warc.gz',
        b'com,example)/ 20171006165521 http://example.com/ warc/revisit - B2LTWWPUOYAH7UIPQ7ZUPQ4VMBSVC36A - - 637 2782 empty-gzips.warc.gz',
        b'com,example)/ 20171006165527 http://example.com/ warc/revisit - B2LTWWPUOYAH7UIPQ7ZUPQ4VMBSVC36A - - 639 5031 empty-gzips.warc.gz'
    ],
    'space_in_target_uri.warc.gz': [
        b'com,example)/weather/forecast/json/mclean%20va?ajax=true 20180625013519 https://www.example.com/weather/forecast/json/McLean%20VA/?ajax=true application/json 200 L43LF2RJAZC64NGZIMRAUFFVJ3S6UW7F - - 398 0 space_in_target_uri.warc.gz'
    ],
    'bracket_in_target_uri.warc.gz': [
        b'com,example)/data.json 20180625013519 https://www.example.com/data.json application/json 200 L43LF2RJAZC64NGZIMRAUFFVJ3S6UW7F - - 328 0 bracket_in_target_uri.warc.gz'
    ],
    # "]" in target URI - redirect capture version
    'bracket_in_target_uri_redirect.arc.gz': [
        b'com,example)/go/url=http:/http[img 20191007055500 http://example.com:80/go/url=http://http[IMG text/html 303 CYKN7HZ4WG26DXAEBMWX3WKC6NKZSRIJ - - 200 147 bracket_in_target_uri_redirect.arc.gz'
    ],
    # chunk-encoded, missing the last "0".
    'missing_chunk_end.warc.gz': [
        b'com,example)/robots.txt 20180803220238 https://example.com/robots.txt text/html 200 W6PEP6F76ZFMLBSNK575R7TWG5STXYBO - - 2406 0 missing_chunk_end.warc.gz'
    ],
    # self-redirect http->https
    'self_redirect.warc.gz': [
        b'org,example)/ 20191021212334 http://example.org/ text/html 301 VMWIPIGAV7UTGNCEHMV6PCGNVW5OL6SG S - 467 273 self_redirect.warc.gz'
    ],
    # contains headers ignored by cdx_writer.handler.HTTPMessage, including
    # header continuation
    'ignored_headers.warc.gz': [
        b'jp,co,jrhokkaido)/press/2013/130920-1.pdf 20200406225837 https://www.jrhokkaido.co.jp/press/2013/130920-1.pdf text/html 200 FGVG2SEVUDFJ374WYEOM6MR3HEV5QXA6 - - 755 281 ignored_headers.warc.gz'
    ],
    # bad URL in location header
    'invalid_location.warc.gz': [
        b'com,example)/favicon.ico 20200406211632 https://example.com/favicon.ico unk 302 3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ - - 369 482 invalid_location.warc.gz'
    ]
}

testdir = py.path.local(__file__).dirpath()
datadir = testdir / "small_warcs"
#sys.path[0:0] = (str(testdir / '..'),)
cdx_writer = __import__('cdx_writer')

@pytest.fixture
def testdata(tmpdir):
    """Function that returns a path of test archive file.
    Currently simple, but we could implement on-the-fly construction of test
    W/ARC file here.

    :param filename: test archive to prepare.
    """
    def prepare_test_data(filename):
        path = datadir.join(filename)
        assert path.exists()
        return path
    return prepare_test_data

def get_cdx_writer_output(tmpdir, args):
    outpath = tmpdir / 'stdout'
    saved_stdout = sys.stdout
    sys.stdout = outpath.open(mode='wb')
    try:
        status = cdx_writer.main(args)
    finally:
        sys.stdout.close()
        output = outpath.read_binary()
        sys.stdout = saved_stdout
    assert status == 0
    return output

CDX_HEADER = b' CDX N b a m s k r M S V g'

@pytest.mark.parametrize(["file", "expected"], warcs_all_records.items())
def test_all_records(file, expected, tmpdir, testdata):
    archive = testdata(file)
    args = ['--all-records', archive.basename]
    with archive.dirpath().as_cwd():
        output = get_cdx_writer_output(tmpdir, args).splitlines()
    assert output[0] == CDX_HEADER
    assert output[1:] == expected

@pytest.mark.parametrize(["file", "expected"], warcs_defaults.items())
def test_defaults(file, expected, tmpdir, testdata):
    '''Test `cdx_writer.py WARC`.'''
    archive = testdata(file)
    args = [archive.basename]
    with archive.dirpath().as_cwd():
        output = get_cdx_writer_output(tmpdir, args).splitlines()
    assert output[0] == CDX_HEADER
    assert output[1:] == expected
