package DJN::Config;

use Class::Std;

use DJN::Sys;

use File::Basename;

# Note that the @HOSTS array contains the names of servers
# that should remain private. For that reason, the server
# names have been obfuscated.

my @HOSTS = ("local", "snargle", "devin", "shrek");

my %name    :ATTR( :name<name>   );
my %source  :ATTR( :name<source> );
my %target  :ATTR( :name<target> );
my %exclude :ATTR( :name<exclude> );

sub BUILD {
    my ($self, $ident, $arg_ref) = @_;

    $source{$ident}  = $arg_ref->{name}     || '';
    $source{$ident}  = $arg_ref->{source}   || '';
    $target{$ident}  = $arg_ref->{target}   || '';
    $exclude{$ident} = $arg_ref->{exclude} || [];
}

sub name {
    my $self = shift;

    return $self->get_name();
}

sub source {
    my $self = shift;

    return $self->get_source();
}

sub target {
    my $self = shift;

    return $self->get_target();
}

sub exclude {
    my $self = shift;

    return $self->get_exclude();
}

sub excluded {
    my $self = shift;

    my $sys  = DJN::Sys->new();
    my $host = $sys->is_local() ? 'local' : $sys->host();
    
    my @excludes = @{ $self->exclude() };

    (grep /($host|\*)/, @excludes) ? return 1 : return 0;
}

sub check {
    my $self    = shift;
    my $verbose = shift || 0;

    my $sys = DJN::Sys->new();

    my $source = $sys->config."/configs/".$self->source();
    my $target = $self->target();
    my $config = $self->name();
    
    return unless -f $source;

    unless (-f $target) {
        print "$config not installed, skipping. \n";

        return;
    }

    chomp(my $diff = `diff $source $target`);

    if ($diff) {
        if ($verbose) {
            print "$config config differs:\n$diff\n\n";
        } else {
            print "$config config differs.\n";
        }
    }

    undef $sys;
    
    return;
}

sub generate {
    my $self = shift;

    my $config = $self->name();
    
    my $sys = DJN::Sys->new();
    
    my $generic = $sys->config()."/generic/".$self->source();
    my $source  = $sys->config()."/configs/".$self->source();

    my $host    = $sys->is_local() ? "local" : $sys->host();
        
    print "Generating configs for $config...\n";
    
    unless (-f $generic) {
        print "Can't find generic config $generic_config! Skipping.\n";

        next;
    }

    unlink $source if -f $source;
    
    my $target_dir = dirname($source);
    system('mkdir', '-p', $target_dir) unless (-d $target_dir);

    _convert_source($generic, $source, $host);

    undef $sys;

    return;
}

sub install {
    my $self = shift;

    my $sys = DJN::Sys->new();

    my $source = $sys->config()."/configs/".$self->source();
    my $target = $self->target();

    my $config = $self->name();

    unless (-f $source) {
        print "Can't find the config for $config:\n\t$source\ndoesn't exist. Skipping.\n";

        next;
    }

    my $target_dir = dirname($target);

    unless (-d $target_dir) {
        system('mkdir', '-p', $target_dir);
    }

    if (-f $target) {
        my $diff = `diff $source $target`;

        return unless ($diff ne '');
    }

    system('cp', '-v', "$source", $target);

    return;
}

sub _convert_source : PRIVATE {
    my $generic = shift;
    my $source  = shift;
    my $host    = shift;
    
    open(my $IFH, "<", $generic) or die "Could not open generic config $generic\n";

    my @lines = <$IFH>;

    close($IFH) or die "Could not close generic config $generic.\n";

    unless ($lines[0] =~ /^\[config:/) {
        print "Generic config file $generic does not start with a '[config:...]' line; skipping.\n";

        next;
    }

    my $line_no = 1;

    my $host_list = {};

    _get_host_list($lines[0], $host_list, $line_no);

    open(my $SFH, '>', $source) or die "Could not open new source file $source.\n";

    shift @lines;
    
    while (my $line = shift @lines) {
        ++$line_no;

        if ($line =~ /\[config:/) {
            _get_host_list($line, $host_list, $line_no);
            next;
        }

        print $SFH $line if ($host_list->{$host});
    }

    close($SFH) or die "Could not close new source file $source.\n";

    return;
}

sub _get_host_list : PRIVATE {
    my $string           = shift;
    my $orig_host_list   = shift;
    my $line_no          = shift;

    $string =~ s{\[config:|\]}{}g;
    $string =~ s{[[:space:]]}{}g;

    my @changes = split(/,/, $string);

    unless ($changes[0] =~ m{^(\+|-)}) {
        for my $host (@HOSTS) {
            $orig_host_list->{$host} = 0;
        }
    }

    for my $change (@changes) {
        if ($change eq '*') {
            for my $host (@HOSTS) {
                $orig_host_list->{$host} = 1;
            }
            next;
        }

        my $value = 1;

        $value = 0 if ($change =~ m{^-});

        $change =~ s{^(\+|-)}{};

        unless (grep /^$change$/, @HOSTS) {
            print "Unknown host $change on line $line_no; ignoring.\n";
            next;
        }

        $orig_host_list->{$change} = $value;
    }

    return;
}

1;
