# {%ONLY POST%}
my $arg = $ARGV[0];
my $li;
# 使用 split 函数将字符串分割成键值对

my @pairs = split /&/, $arg;
foreach my $pair (@pairs) {
    my ($key, $value) = split /=/, $pair;
    $li{$key} = $value;
}
my $num1 = int($li{'first'});
my $num2 = int($li{'second'});
my $op = int($li{'rule'});
my $res;
if($op eq 'add'){
    $res = $num1 + $num2;
}
else{
    $res = $num1 * $num2;
}
# 输出
print "{\"result\":\"$res\",\"tool\":\"result by perl\"}\n";
