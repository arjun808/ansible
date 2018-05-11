import jenkins.model.*
import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.common.*
import com.cloudbees.plugins.credentials.domains.*
import com.cloudbees.plugins.credentials.impl.*
import com.cloudbees.jenkins.plugins.sshcredentials.impl.*
import hudson.plugins.sshslaves.*;

String keyfile = """
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAvhV1O25Mb7+rtflrX3Uv4k+Ub8M6CXF9KGSsrvGP7zgnvVWaaBD6YpHzMNKT
vSUp23NTawt6/dr335YlGfUDOo6sIeWLPD29JY7yulPCyJCiTsZIpiHH+1o+uOWyj4zLhnrWp4zJ
c6PJmG3V9iRoHqjJOdg8SD8EQ17sAz3VuuZn6REHzjhXLpnzazQ3pax6rMtMg5XfaSfJ0Rzz5U+R
9kOQHP3PVenGimK8Z4EY+Yh7juSB8lk53y7o+bnFwmkNRMfw4QBsZUyhPrXzFwJu304n8CvrCpbk
qpT55dmZNPHPZK2N5+3Ws2OeJV3dloX5yhUr1K0IsvkwFcTbNYtG2QIDAQABAoIBAQC4csYBV3Rg
c5NBz7d7N5GxfxtAoCZvB2s1iQtv7wOGU+1r8ecU2HS+tXVQiOXHgoptYikuFEPSlWo10dJKr8/k
QJGTitRjLl2eVmn+mEzIpmB5JDtWyizuIJIAhROR7EOKSSSGDT1mMybp/JrEcGuAZLRupv9H865F
WZSXSKde5Yr35WhsNAORHMEdXR4CdHtB1z1BDjdEdFZzt+kKo2HHkgGysRsaHr1qt13wNR76qaMN
mzMy2s/Z41Yh5W+cQ1/LTobmUHj6t5SzbAgZ8Pty+KASIkAdyTpSX/TjHlny+QVjw8FGHXmQntnO
yLvJF9rCQLD/t7Fs6aKEgb3pY6ghAoGBAPN6jbQj2i0yQ6+YQpyCB19Cf8V0lLfFAcilPbfDgEjr
L5HJ9KEYkXXbLrxdHusu9eSbTGIvGeHHtUwreUN9DQ1PBo7M9PeZWytcjH/NZrX2ZKyrbH7tdcKl
+3SQl+3zPj6nS0985EeniPXxQlo9YmlA/qqgYSxxkCnItglEevTdAoGBAMfb8yF8FqfBSgKiTFop
JmBUw7OYkTo+mhLBM632yHbh24KTmBy3Lrml/2I9wM5xfCkW8gsUSh0VIq1MH8yhwfE7WPvoIwAb
jtpv9FjtrUB/he8QaAsCd4dNVPwpnV3My8Hlf2aPsNyDa0CrD1ZqdU7ILaeQ5aGb6olW97xolWwt
AoGARAYrbPbPT+1JJ9f8VEmn0Z98nygRHL633tz7v0mpn7XFlo+7/v4kNa9FAW9q4f4+yN3ym0PZ
kVEAgAVtXcOkT+GSTXdJwZtg815qCpLSbWgnfG5wY43oZreE5242ZE6fR1XqHo0gIjzWcRA0n42i
3xE/lWA1hfs8cdAXu8McLykCgYEAwvViVNWxW++HfM5JYOInV20YgsdfU8vhjE3/VcIYhy+Ha/cC
OXDQGbU+TN0kib3WelaxwfEG4xvM+fP6SSm6ANH92a33BpHbZmYzm9QuX26GflAoziSX6Nqc/max
5eBzGy/+eVPOGS3xn+G+UnQC/tjzADSubFmmDldRzu7OY/kCgYBDv7Pk1Ow4p8SKVmiiGNPAmBfE
Zw1Y8GGrbE4Ql2ZkHv0xPt9aEURF/H3yCLrO7MZr5PAqZS0OR1wAqFliIWkOm+4f9FTj6MhyoL9z
kntD5vu8CwwhoFqEOLZqMz/IznCBXE51VdlY0Ud3JELj9FT5StYekyazvjkCKdpuzlVFEQ==
-----END RSA PRIVATE KEY-----
"""


domain = Domain.global()
store = Jenkins.instance.getExtensionList('com.cloudbees.plugins.credentials.SystemCredentialsProvider')[0].getStore()

priveteKey = new BasicSSHUserPrivateKey(
CredentialsScope.GLOBAL,
"jenkins",
"ec2-user",
new BasicSSHUserPrivateKey.DirectEntryPrivateKeySource(keyfile),
"ansible",
"this is a credential for connecting node"
)


store.addCredentials(domain, priveteKey)
