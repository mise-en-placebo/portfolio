package DJN::Sys;

use Class::Std;

use Env;

my %host       : ATTR( :name<host> );
my %user       : ATTR( :name<user> :default<'djn'>);
my %sysroot    : ATTR( :name<sysroot> );

sub BUILD {
    my ($self, $ident, $arg_ref) = @_;

    chomp($host{$ident} = $arg_ref->{host}    || `hostname`);
    $user{$ident}       = $arg_ref->{user}    || $USER;

    # Normally, I keep most of my source files in the `/src`
    # path on any device I control of the root of
    # directory. On devices/servers where I do not, I keep
    # my sources in my home directory. 
    #
    # For the purposes of the portfolio, I'll just assume
    # that the `config` calling script is being called from
    # the directory containing it in the portfolio.

    # Original
    # $sysroot{$ident}    = $self->is_local() ? '/src' : "$HOME/src";
    # Portfolio
    $sysroot{$ident}    = '.';
}

sub is_local {
    my $self = shift;

    if ( -d '/src' ) {
        my $owner = getpwuid((stat('/src'))[4]);

        my $mode = int((sprintf "%03o", (stat('/src'))[2] & 07777)/100);

        return 1 if $owner eq $self->user() && $mode == 7;
    }
    
    return 0;
}

sub host {
    my $self = shift;

    return $self->get_host();
}

sub user {
    my $self = shift;

    return $self->get_user();
}

sub sysroot {
    my $self = shift;

    return $self->get_sysroot();
}

sub source {
    my $self = shift;

    return $self->get_sysroot()."/source";
}

sub config {
    my $self = shift;

    # For the portfolio, since everything is contained in
    # the 'configs' directory, I had to rename 'config/' to
    # 'configs/'.
    
    return $self->get_sysroot()."/configs";
}

sub docs {
    my $self = shift;

    return $self->get_sysroot()."/docs";
}

sub bin {
    my $self = shift;

    return $self->get_sysroot()."/bin";
}

sub lib {
    my $self = shift;

    return $self->get_sysroot()."/lib";
}

1;
