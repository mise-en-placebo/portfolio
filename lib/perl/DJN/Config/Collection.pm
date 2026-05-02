package DJN::Config::Collection;

use UNIVERSAL;

use Class::Std;

use DJN::Sys;

###
### Attributes
###

my %name    :ATTR( :name<name> );
my %configs :ATTR( :name<configs> );

###
### Builders
###

sub BUILD {
    my ($self, $ident, $arg_ref) = @_;

    $configs{$ident} = $arg_ref->{configs} || [];
}

### 
### Subroutintes
### 

sub configs {
    my $self = shift;

    return @{ $self->get_configs() };
}

sub configs_ref {
    my $self = shift;

    return $self->get_configs();
};

sub push {
    my $self = shift;

    for (@_) {
        if ($_->isa('DJN::Config::Collection')) {
            push( @{ $self->configs_ref() }, $_->configs() );
        } elsif ($_->isa('DJN::Config')) {
            push( @{ $self->configs_ref() }, $_);
        } else {
            print "Unknown object $_; skipping.\$";
            next;
        }
    }
    
    return;
}

sub list {
    my $self = shift;

    my $verbose = shift || 0;

    my $sys = DJN::Sys->new();

    for my $config ($self->configs()) {
        print $config->name()."\n";

        if ($verbose) {
            my $source = $sys->config()."/configs/".$config->source();
            my $target = $config->target();

            print "\t\tsource: $source\n\t\ttarget: $target\n\n"
        }        
    }

    undef $sys;

    return;
}

sub check {
    my $self = shift;

    my $verbose = shift || 0;

    for my $config ($self->configs()) {
        $config->check($verbose);
    }

    return;
}

sub generate {
    my $self = shift;

    for my $config ($self->configs()) {
        $config->generate();
    }

    return;
}

sub install {
    my $self = shift;

    for my $config ($self->configs()) {
        $config->install();
    }

    return;
}

1;
